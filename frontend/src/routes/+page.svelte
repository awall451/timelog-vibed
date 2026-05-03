<script lang="ts">
  import Dashboard from '$lib/components/Dashboard.svelte';
  import DemoLanding from '$lib/components/DemoLanding.svelte';
</script>

{#if import.meta.env.VITE_DEMO_MODE}
  <DemoLanding />
{:else}
  <Dashboard />
{/if}
