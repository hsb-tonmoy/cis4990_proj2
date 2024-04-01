<script lang="ts">
  import VoiceRecorder from "./lib/components/VoiceRecorder.svelte";
  import history from "./lib/assets/history.svg";

  let userSpeech: string | null = null;
  let chatResponse: string | null = null;

  let isLoading: boolean = false;

  let audio: HTMLAudioElement | null = null;

  async function sendAudioToAPI(event: CustomEvent<Blob[]>) {
    isLoading = true;
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
          const audioResponse = response.clone();
          const audioData = await audioResponse.arrayBuffer();
          const audioBlob = new Blob([audioData], { type: "audio/mpeg" });
          const audioUrl = URL.createObjectURL(audioBlob);
          audio = new Audio(audioUrl);
          audio.play();
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
</script>

<main class="relative w-full h-screen font-primary">
  <div class="absolute bottom-10 xl:top-10 right-5">
    <button class="w-20"
      ><img src={history} alt="History" class="object-cover" /></button
    >
  </div>
  <div
    class="container mx-auto flex flex-col items-center px-8 py-10 md:py-20 xl:py-30 h-full"
  >
    <h1 class="text-3xl md:text-5xl xl:text-6xl text-[#050A30] text-center">
      Karen. The Voice Assistant
    </h1>
    <h6 class="italic text-xs md:text-sm mt-2">
      Click on the microphone to start speaking
    </h6>
    <div class="recorder mt-20 md:mt-40 xl:mt-60">
      <VoiceRecorder
        bind:isLoading
        on:start={() => {
          audio?.pause();
          audio = null;
          userSpeech = null;
          chatResponse = null;
        }}
        on:stop={sendAudioToAPI}
      />
    </div>
    {#if userSpeech}
      <div class="userSpeech text-base md:text-xl xl:text-2xl mt-10">
        <span class="text-[#050A30] italic mb-2">You said: </span>
        <span class="">{userSpeech}</span>
      </div>
    {/if}
    {#if chatResponse}
      <div class="userSpeech text-base md:text-xl xl:text-2xl mt-4">
        <span class="text-[#050A30] italic mb-2">ChatGPT said: </span>
        <span class="">{chatResponse}</span>
      </div>
    {/if}
  </div>
</main>

<style lang="postcss">
  main {
    background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  }
</style>
