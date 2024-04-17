<script lang="ts">
  import { onMount, createEventDispatcher, onDestroy } from "svelte";
  import mic from "../assets/mic.png";
  import stop from "../assets/stop.png";

  import { MediaRecorder, register } from "extendable-media-recorder";
  import { connect } from "extendable-media-recorder-wav-encoder";

  onMount(async () => {
    await register(await connect());
  });

  const dispatch = createEventDispatcher();

  export let isLoading: boolean = false;
  export let isPlaying: boolean = false;

  let stream: MediaStream | null = null;
  let mediaRecorder: any = null;
  let chunks: Blob[] = [];
  let isRecording = false;
  let silenceTimer: any = null;
  const silenceThreshold = 1;
  const silenceDuration = 3000;

  async function startRecording() {
    isRecording = true;
    chunks = [];
    dispatch("start");

    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/wav" });

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
    if (isRecording && mediaRecorder) {
      isRecording = false;
      mediaRecorder.stop();
      mediaRecorder = null;
      dispatch("stopRecording", chunks);
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
        stream = null;
      }
    }
  }
  async function stopPlayback() {
    isPlaying = false;
    dispatch("stopPlayback");
  }

  onDestroy(() => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
    }
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
  });
</script>

{#if !isLoading}
  <button
    class="w-40 h-40 bg-cover bg-no-repeat transition-all duration-300 ease-in-out rounded-full border-4 border-[#DF3A5C] {isRecording
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
{:else if isPlaying}
  <button
    class="w-40 h-40 bg-cover bg-no-repeat transition-all duration-300 ease-in-out rounded-full border-4 border-[#DF3A5C]"
    style="background-image: url({stop})"
    on:click={stopPlayback}
  ></button>
{:else}
  <button
    class="loading w-40 h-40 bg-cover bg-no-repeat transition-all duration-300 ease-in-out rounded-full border-4 border-[#DF3A5C]"
    disabled
  ></button>
{/if}

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

  .loading {
    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"><path fill="none" stroke="%23DF3A5C" stroke-dasharray="15" stroke-dashoffset="15" stroke-linecap="round" stroke-width="2" d="M12 3C16.9706 3 21 7.02944 21 12"><animate fill="freeze" attributeName="stroke-dashoffset" dur="0.3s" values="15;0"/><animateTransform attributeName="transform" dur="1.5s" repeatCount="indefinite" type="rotate" values="0 12 12;360 12 12"/></path></svg>');
  }
</style>
