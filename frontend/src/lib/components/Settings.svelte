<script lang="ts">
  import { writable } from "svelte/store";
  import { Drawer, Radio, CloseButton } from "flowbite-svelte";
  import { backIn } from "svelte/easing";
  let closed = true;
  let transitionParams = {
    x: 384,
    duration: 500,
    easing: backIn,
  };

  export let voice = writable("female");
  export let name: string = "Karen";
  let expertise = writable("anything");
  let language = writable("en");

  function updateSettings() {
    const settings = {
      voice: $voice,
      expertise: $expertise,
      language: $language,
    };
    fetch("/update-settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    })
      .then((response) => response.json())
      .then((data) => console.log("Settings updated:", data))
      .catch((error) => console.error("Failed to update settings:", error));
  }

  voice.subscribe(() => updateSettings());
  expertise.subscribe(() => updateSettings());
  language.subscribe(() => updateSettings());
</script>

<div class="absolute bottom-10 xl:top-10 right-10">
  <button
    on:click={() => (closed = false)}
    class="w-8 text-[#050A30] dark:text-[#f8f9fa]"
    ><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
      ><path
        fill="currentColor"
        d="m9.25 22l-.4-3.2q-.325-.125-.612-.3t-.563-.375L4.7 19.375l-2.75-4.75l2.575-1.95Q4.5 12.5 4.5 12.338v-.675q0-.163.025-.338L1.95 9.375l2.75-4.75l2.975 1.25q.275-.2.575-.375t.6-.3l.4-3.2h5.5l.4 3.2q.325.125.613.3t.562.375l2.975-1.25l2.75 4.75l-2.575 1.95q.025.175.025.338v.674q0 .163-.05.338l2.575 1.95l-2.75 4.75l-2.95-1.25q-.275.2-.575.375t-.6.3l-.4 3.2zM11 20h1.975l.35-2.65q.775-.2 1.438-.587t1.212-.938l2.475 1.025l.975-1.7l-2.15-1.625q.125-.35.175-.737T17.5 12q0-.4-.05-.787t-.175-.738l2.15-1.625l-.975-1.7l-2.475 1.05q-.55-.575-1.212-.962t-1.438-.588L13 4h-1.975l-.35 2.65q-.775.2-1.437.588t-1.213.937L5.55 7.15l-.975 1.7l2.15 1.6q-.125.375-.175.75t-.05.8q0 .4.05.775t.175.75l-2.15 1.625l.975 1.7l2.475-1.05q.55.575 1.213.963t1.437.587zm1.05-4.5q1.45 0 2.475-1.025T15.55 12q0-1.45-1.025-2.475T12.05 8.5q-1.475 0-2.488 1.025T8.55 12q0 1.45 1.013 2.475T12.05 15.5M12 12"
      /></svg
    ></button
  >
</div>

<Drawer
  placement="right"
  transitionType="fly"
  {transitionParams}
  bind:hidden={closed}
  id="settings"
  width="w-96"
  class="overflow-y-auto z-50 py-4 bg-white dark:bg-[#273144]"
>
  <div class="flex items-center justify-between">
    <h6 class="text-[#050A30] dark:text-[#f8f9fa] text-lg font-medium">
      Supercharge {name}!
    </h6>
    <CloseButton
      on:click={() => (closed = true)}
      class="mb-4 dark:text-white"
    />
  </div>
  <div class="px-4">
    <form action="" class="mt-4">
      <p class="mb-4 font-semibold text-gray-900 dark:text-white">
        Switch Voice
      </p>
      <ul
        class="items-center w-full rounded-lg border border-gray-200 sm:flex dark:bg-gray-800 dark:border-gray-600 divide-x rtl:divide-x-reverse divide-gray-200 dark:divide-gray-600"
      >
        <li class="w-full">
          <Radio bind:group={$voice} value="male" class="p-3">Male</Radio>
        </li>
        <li class="w-full">
          <Radio bind:group={$voice} value="female" class="p-3">Female</Radio>
        </li>
      </ul>

      <p class="mt-6 mb-4 font-semibold text-[#050A30] dark:text-[#f8f9fa]">
        Choose Expertise
      </p>
      <ul
        class="w-48 bg-white rounded-lg border border-gray-200 dark:bg-gray-800 dark:border-gray-600 divide-y divide-gray-200 dark:divide-gray-600"
      >
        <li>
          <Radio class="p-3" bind:group={$expertise} value="anything"
            >General</Radio
          >
        </li>
        <li>
          <Radio class="p-3" bind:group={$expertise} value="science"
            >Science</Radio
          >
        </li>
        <li>
          <Radio class="p-3" bind:group={$expertise} value="programming"
            >Programming</Radio
          >
        </li>
        <li>
          <Radio class="p-3" bind:group={$expertise} value="literature"
            >Literature</Radio
          >
        </li>
        <li>
          <Radio class="p-3" bind:group={$expertise} value="history"
            >History</Radio
          >
        </li>
        <li>
          <Radio class="p-3" bind:group={$expertise} value="music">Music</Radio>
        </li>
        <li>
          <Radio class="p-3" bind:group={$expertise} value="sports"
            >Sports</Radio
          >
        </li>
      </ul>
      <p class="mt-6 mb-4 font-semibold text-[#050A30] dark:text-[#f8f9fa]">
        Change/Translate Language
      </p>
      <ul
        class="w-48 bg-white rounded-lg border border-gray-200 dark:bg-gray-800 dark:border-gray-600 divide-y divide-gray-200 dark:divide-gray-600"
      >
        <li>
          <Radio class="p-3" bind:group={$language} value="en">English</Radio>
        </li>
        <li>
          <Radio class="p-3" bind:group={$language} value="es">Spanish</Radio>
        </li>
        <li>
          <Radio class="p-3" bind:group={$language} value="fr">French</Radio>
        </li>
        <li>
          <Radio class="p-3" bind:group={$language} value="de">German</Radio>
        </li>
        <li>
          <Radio class="p-3" bind:group={$language} value="it">Italian</Radio>
        </li>
      </ul>
    </form>
  </div>
</Drawer>
