<script lang="ts">
  import mic from "../assets/mic.png";
  import stop from "../assets/stop.png";

  export let userSpeech: string | null = null;

  let stream: MediaStream | null = null;
  let mediaRecorder: any = null;
  let chunks: Blob[] = [];
  let isRecording = false;
  let silenceTimer: any = null;
  const silenceThreshold = 1;
  const silenceDuration = 3000;

  async function startRecording() {
    userSpeech = null;
    isRecording = true;
    chunks = [];

    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

    mediaRecorder.addEventListener("dataavailable", (event: BlobEvent) => {
      chunks.push(event.data);
    });

    mediaRecorder.addEventListener("stop", () => {
      stream?.getTracks().forEach((track) => track.stop());
    });

    const audioContext = new AudioContext();
    const sourceNode = audioContext.createMediaStreamSource(stream);
    const analyserNode = audioContext.createAnalyser();
    sourceNode.connect(analyserNode);

    const bufferLength = analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function detectSilence() {
      analyserNode.getByteFrequencyData(dataArray);
      const avgVolume =
        dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
      const isSilent = avgVolume < silenceThreshold;

      if (isSilent) {
        if (!silenceTimer) {
          silenceTimer = setTimeout(() => {
            stopRecording();
          }, silenceDuration);
        }
      } else {
        clearTimeout(silenceTimer);
        silenceTimer = null;
      }

      if (isRecording) {
        requestAnimationFrame(detectSilence);
      }
    }

    mediaRecorder.start(500); // Capture audio data every 500 ms
    requestAnimationFrame(detectSilence);
  }

  async function stopRecording() {
    isRecording = false;
    mediaRecorder?.stop();
    await sendAudioToAPI();
  }

  async function sendAudioToAPI() {
    const audioBlob = new Blob(chunks, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio", audioBlob);

    fetch("/speech-to-text", {
      method: "POST",
      body: formData,
      headers: {
        "Cache-Control": "no-cache",
      },
    })
      .then(async (response) => {
        const data = await response.json();
        userSpeech = data.text;
      })
      .catch((error) => {
        console.error("Error sending audio to API:", error);
      });
  }
</script>

<button
  class="w-40 h-40 mt-60 bg-cover bg-no-repeat transition-all duration-300 ease-in-out rounded-full border border-[#ec7986] {isRecording
    ? 'recording'
    : 'hover:scale-110'}"
  style="background-image: url({isRecording ? stop : mic})"
  on:click={() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }}
></button>

<style lang="postcss">
  .recording {
    animation: pulse 0.8s infinite;
    animation-timing-function: linear;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 #ec7986;
    }
    70% {
      box-shadow: 0 0 0 10px #ec7986;
    }
    100% {
      box-shadow: 0 0 0 0 #ec7986;
    }
  }
</style>
