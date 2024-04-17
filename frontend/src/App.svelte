<script lang="ts">
  import WaveSurfer from "wavesurfer.js";
  import VoiceRecorder from "./lib/components/VoiceRecorder.svelte";

  let userSpeech: string | null = null;
  let chatResponse: string | null = null;

  let isLoading: boolean = false;
  let isPlaying: boolean = false;

  let wavesurfer: WaveSurfer | null = null;

  let errorOccurred: boolean = false;

  async function initializeWavesurfer() {
    if (!wavesurfer) {
      wavesurfer = WaveSurfer.create({
        container: "#waveform",
        waveColor: "#ff758f",
        progressColor: "#c9184a",
        cursorColor: "#ffccd5",
        barWidth: 2,
        barRadius: 3,
        normalize: true,
      });
    }
  }

  async function sendAudioToAPI(event: CustomEvent<Blob[]>) {
    isLoading = true;
    errorOccurred = false;
    const audioBlob = new Blob(event.detail, { type: "audio/wav" });
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
        isLoading = false;
        userSpeech = data.text;
        sendTextToAPI(data.text);
      })
      .catch((error) => {
        console.error("Error sending audio to API:", error);
        errorOccurred = true;
      })
      .finally(() => {
        isLoading = false;
      });
  }

  async function sendTextToAPI(text: string) {
    isLoading = true;
    fetch("/send-to-chatgpt", {
      method: "POST",
      body: JSON.stringify({ text: text }),
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
      },
    })
      .then(async (response) => {
        const contentType = response.headers.get("Content-Type");
        const chatResponseHeader = response.headers.get("chat_response");

        if (contentType?.includes("audio/mpeg")) {
          const audioData = await response.arrayBuffer();
          const audioBlob = new Blob([audioData], { type: "audio/mpeg" });
          const audioUrl = URL.createObjectURL(audioBlob);
          await initializeWavesurfer();
          wavesurfer?.load(audioUrl);
          wavesurfer?.play();
          isPlaying = true;
        }

        if (chatResponseHeader) {
          chatResponse = chatResponseHeader;
        }
        isLoading = false;
      })
      .catch((error) => {
        console.error("Error sending audio to API:", error);
      });
  }

  $: {
    wavesurfer?.on("init", () => {
      wavesurfer?.play();
    });
  }

  $: {
    wavesurfer?.on("finish", () => {
      isPlaying = false;
    });
  }

  function stopPlayBack() {
    isPlaying = false;
    wavesurfer?.playPause();
    wavesurfer?.destroy();
    wavesurfer = null;
    userSpeech = null;
    chatResponse = null;
  }
</script>

<main class="main-bg dark:main-bg-dark relative w-full h-screen font-primary">
  <div class="absolute bottom-10 xl:top-10 right-10">
    <button class="w-8 text-[#050A30] dark:text-[#f8f9fa]"
      ><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        ><path
          fill="currentColor"
          d="m9.25 22l-.4-3.2q-.325-.125-.612-.3t-.563-.375L4.7 19.375l-2.75-4.75l2.575-1.95Q4.5 12.5 4.5 12.338v-.675q0-.163.025-.338L1.95 9.375l2.75-4.75l2.975 1.25q.275-.2.575-.375t.6-.3l.4-3.2h5.5l.4 3.2q.325.125.613.3t.562.375l2.975-1.25l2.75 4.75l-2.575 1.95q.025.175.025.338v.674q0 .163-.05.338l2.575 1.95l-2.75 4.75l-2.95-1.25q-.275.2-.575.375t-.6.3l-.4 3.2zM11 20h1.975l.35-2.65q.775-.2 1.438-.587t1.212-.938l2.475 1.025l.975-1.7l-2.15-1.625q.125-.35.175-.737T17.5 12q0-.4-.05-.787t-.175-.738l2.15-1.625l-.975-1.7l-2.475 1.05q-.55-.575-1.212-.962t-1.438-.588L13 4h-1.975l-.35 2.65q-.775.2-1.437.588t-1.213.937L5.55 7.15l-.975 1.7l2.15 1.6q-.125.375-.175.75t-.05.8q0 .4.05.775t.175.75l-2.15 1.625l.975 1.7l2.475-1.05q.55.575 1.213.963t1.437.587zm1.05-4.5q1.45 0 2.475-1.025T15.55 12q0-1.45-1.025-2.475T12.05 8.5q-1.475 0-2.488 1.025T8.55 12q0 1.45 1.013 2.475T12.05 15.5M12 12"
        /></svg
      ></button
    >
  </div>
  <div
    class="container mx-auto flex flex-col items-center px-8 py-10 md:py-20 xl:py-30 h-full"
  >
    <h1
      class="text-3xl md:text-5xl xl:text-6xl text-[#050A30] dark:text-[#f8f9fa] text-center"
    >
      Karen. The Voice Assistant
    </h1>
    <h6 class="italic text-xs md:text-sm mt-2 dark:text-[#e9ecef]">
      Click on the microphone to start speaking
    </h6>
    <div class="recorder mt-20 md:mt-40 xl:mt-60">
      <VoiceRecorder
        bind:isLoading
        bind:isPlaying
        on:start={stopPlayBack}
        on:stopRecording={sendAudioToAPI}
        on:stopPlayback={stopPlayBack}
      />
    </div>
    {#if !errorOccurred}
      {#if userSpeech}
        <div
          class="text-[#050A30] dark:text-[#f8f9fa] userSpeech text-base md:text-xl xl:text-2xl mt-10"
        >
          <span class="italic dark:font-semibold mb-2">You said: </span>
          <span class="">{userSpeech}</span>
        </div>
      {/if}
      {#if chatResponse}
        <div
          class="text-[#050A30] dark:text-[#f8f9fa] karenSpeech text-base md:text-xl xl:text-2xl mt-4"
        >
          <span class="italic dark:font-semibold mb-2">Karen said: </span>
          <span class="">{chatResponse}</span>
        </div>
      {/if}
    {:else}
      <div class="mt-10">
        <span class="text-red-600 text-base md:text-xl xl:text-2xl mt-4">
          An error occurred. Please try again.
        </span>
      </div>
    {/if}
    <div id="waveform" class="mt-4 w-96 h-48"></div>
  </div>
</main>

<style lang="postcss">
</style>
