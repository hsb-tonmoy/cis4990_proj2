<script lang="ts">
  import mic from "../assets/mic.png";
  import stop from "../assets/stop.png";

  let mediaRecorder: MediaRecorder | null = null;
  let audioChunks: Blob[] = [];
  let isRecording = false;

  function startRecording() {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        // console.log("Media stream obtained:", stream);
        mediaRecorder = new MediaRecorder(stream, {
          mimeType: "audio/ogg",
        });
        mediaRecorder.addEventListener("dataavailable", handleDataAvailable);
        mediaRecorder.start();
        isRecording = true;
      })
      .catch((error) => {
        console.error("Error accessing media devices:", error);
      });
  }

  function stopRecording() {
    mediaRecorder?.stop();
    isRecording = false;
  }

  function handleDataAvailable(event: BlobEvent) {
    audioChunks.push(event.data);
  }

  function sendAudioToAPI() {
    const audioBlob = new Blob(audioChunks, { type: "audio/ogg" });
    const formData = new FormData();
    formData.append("audio", audioBlob);

    fetch("/speech-to-text", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        // Handle the API response
        const data = response.json();
        console.log("API response:", data);
      })
      .catch((error) => {
        console.error("Error sending audio to API:", error);
      });
  }

  // For testing audio record, add a playback

  function playAudio() {
    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
  }
</script>

<button
  class="mic-button"
  on:click={() => {
    if (isRecording) {
      stopRecording();
      sendAudioToAPI();
    } else {
      startRecording();
    }
  }}
  ><img
    src={isRecording ? stop : mic}
    alt="Microphone"
    class="object-cover w-40 mt-60"
  /></button
>

<button class="bg-blue p-4 text-white" on:click={playAudio}>Test Audio</button>

<style lang="postcss">
  .mic-button {
    transition: transform 0.3s ease;
  }
  .mic-button:hover {
    transform: scale(1.1);
  }
</style>
