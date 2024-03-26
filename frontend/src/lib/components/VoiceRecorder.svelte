<script lang="ts">
  import { MediaRecorder, register } from "extendable-media-recorder";
  import { connect } from "extendable-media-recorder-wav-encoder";
  import mic from "../assets/mic.png";
  import stop from "../assets/stop.png";
  import { onMount } from "svelte";

  let stream: MediaStream | null = null;
  let media: Blob[] = [];
  let mediaRecorder: any = null;
  let blob: Blob | null = null;
  let isRecording = false;

  onMount(async () => {
    register(await connect());
  });

  async function startRecording() {
    isRecording = true;
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/wav" });
    mediaRecorder.ondataavailable = (e: BlobEvent) => media.push(e.data);
    mediaRecorder.onstop = function () {
      blob = new Blob(media, { type: "audio/wav" });
      media = [];
      stream?.getTracks().forEach((track) => track.stop());
    };
    mediaRecorder.start();
  }

  async function stopRecording() {
    mediaRecorder?.stop();
    isRecording = false;
    await sendAudioToAPI();
  }

  async function sendAudioToAPI() {
    const audioBlob = new Blob(blob ? [blob] : [], { type: "audio/wav" });
    const formData = new FormData();
    formData.append("audio", audioBlob);

    fetch("/speech-to-text", {
      method: "POST",
      body: formData,
      headers: {
        "cache-control": "no-cache",
      },
    })
      .then(async (response) => {
        // Handle the API response
        const data = await response.json();
        console.log("API response:", data);
      })
      .catch((error) => {
        console.error("Error sending audio to API:", error);
      });
  }

  // For testing audio record, add a playback

  function playAudio() {
    if (blob) {
      const audioURL = URL.createObjectURL(blob);
      const audio = new Audio(audioURL);
      audio.play();
    } else {
      console.log("No audio recorded yet.");
    }
  }
</script>

<button
  class="mic-button"
  on:click={() => {
    if (isRecording) {
      stopRecording();
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
