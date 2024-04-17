<script lang="ts">
  import type { Writable } from "svelte/store";
  import { slide } from "svelte/transition";
  import { quintOut } from "svelte/easing";
  import WaveSurfer from "wavesurfer.js";
  import { Toast } from "flowbite-svelte";
  import { CloseCircleSolid } from "flowbite-svelte-icons";
  import Settings from "./lib/components/Settings.svelte";
  import VoiceRecorder from "./lib/components/VoiceRecorder.svelte";

  let userSpeech: string | null = null;
  let chatResponse: string | null = null;

  let isLoading: boolean = false;
  let isPlaying: boolean = false;

  let wavesurfer: WaveSurfer | null = null;

  let errorOccurred: boolean = false;

  let voice: Writable<string>;

  let name: string = "Karen";

  $: if ($voice === "male") {
    name = "Darren";
  } else {
    name = "Karen";
  }

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
        triggerToast();
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
        triggerToast();
      })
      .finally(() => {
        isLoading = false;
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

  let counter = 10;

  function triggerToast() {
    errorOccurred = true;
    counter = 10;
    timeout();
  }

  function timeout() {
    if (--counter > 0) return setTimeout(timeout, 1000);
    errorOccurred = false;
  }
</script>

<svelte:head>
  <title>{name} - The Voice Assistant</title>
</svelte:head>

<main class="main-bg dark:main-bg-dark relative w-full h-screen font-primary">
  <Toast
    position="bottom-right"
    color="red"
    bind:open={errorOccurred}
    transition={slide}
    params={{ delay: 250, duration: 300, easing: quintOut }}
  >
    <svelte:fragment slot="icon">
      <CloseCircleSolid class="w-5 h-5" />
      <span class="sr-only">Error icon</span>
    </svelte:fragment>
    Please try again
  </Toast>

  <Settings bind:voice bind:name />
  <div
    class="container mx-auto flex flex-col items-center px-8 py-10 md:py-20 xl:py-30 h-full"
  >
    <h1
      class="text-3xl md:text-5xl xl:text-6xl text-[#050A30] dark:text-[#f8f9fa] text-center"
    >
      {name}. The Voice Assistant
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
          <span class="italic dark:font-semibold mb-2">{name} said: </span>
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
