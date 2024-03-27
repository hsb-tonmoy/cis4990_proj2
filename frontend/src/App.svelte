<script lang="ts">
  import VoiceRecorder from "./lib/components/VoiceRecorder.svelte";
  import history from "./lib/assets/history.svg";

  let userSpeech: string | null = null;
  let chatResponse: string | null = null;

  async function sendAudioToAPI(event: CustomEvent<Blob[]>) {
    const audioBlob = new Blob(event.detail, { type: "audio/wav" });
    const formData = new FormData();
    formData.append("audio", audioBlob);

    fetch("/send-to-chatgpt", {
      method: "POST",
      body: formData,
      headers: {
        "Cache-Control": "no-cache",
      },
    })
      .then(async (response) => {
        const contentType = response.headers.get("Content-Type");
        const userInputHeader = response.headers.get("user_input");
        const chatResponseHeader = response.headers.get("chat_response");

        if (contentType?.includes("audio/mpeg")) {
          const audioResponse = response.clone();
          const audioData = await audioResponse.arrayBuffer();
          const audioBlob = new Blob([audioData], { type: "audio/mpeg" });
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          audio.play();
        }

        if (userInputHeader) {
          userSpeech = userInputHeader;
        }
        if (chatResponseHeader) {
          chatResponse = chatResponseHeader;
        }
      })
      .catch((error) => {
        console.error("Error sending audio to API:", error);
      });
  }
</script>

<main class="relative w-full h-screen font-primary">
  <div class="absolute top-10 right-5">
    <button class="w-20"
      ><img src={history} alt="History" class="object-cover" /></button
    >
  </div>
  <div class="container mx-auto flex flex-col items-center py-40 h-full">
    <h1 class="text-6xl text-[#050A30]">Karen. The Voice Assistant</h1>
    <h6 class="italic text-sm mt-2">
      Click on the microphone to start speaking
    </h6>
    <div class="recorder">
      <VoiceRecorder
        on:start={() => {
          userSpeech = null;
          chatResponse = null;
        }}
        on:stop={sendAudioToAPI}
      />
    </div>
    {#if userSpeech}
      <div class="userSpeech text-2xl mt-10">
        <span class="text-[#050A30] italic mb-2">You said: </span>
        <span class="">{userSpeech}</span>
      </div>
    {/if}
    {#if chatResponse}
      <div class="userSpeech text-2xl mt-4">
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
