<script lang="ts">
	/**
	 * MINIMAL DocumentsTab for debugging
	 */
	import { currentProjectId } from '$lib/stores/projects';
</script>

<div class="documents-tab">
	<h1>Documents Tab - Minimal Test</h1>
	<p>Current Project ID: {$currentProjectId}</p>
	<p>If you can see this, the tab component is rendering!</p>
</div>

<style>
	.documents-tab {
		padding: 2rem;
		color: white;
	}
</style>
