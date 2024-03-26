<script lang="ts">
  import VoiceRecorder from "./lib/components/VoiceRecorder.svelte";
  import history from "./lib/assets/history.svg";

  let userSpeech: string | null = null;
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
      <VoiceRecorder bind:userSpeech />
    </div>
    {#if userSpeech}
      <div class="userSpeech text-2xl mt-10">
        <span class="text-[#050A30] italic mb-2">You said:</span>
        <span class="">{userSpeech}</span>
      </div>
    {/if}
  </div>
</main>

<style lang="postcss">
  main {
    background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  }
</style>
