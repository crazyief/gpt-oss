declare module 'svelte-virtual-list' {
	import { SvelteComponentTyped } from 'svelte';

	export interface VirtualListProps {
		items: any[];
		height?: string | number;
		itemHeight?: number;
		start?: number;
		end?: number;
	}

	export default class VirtualList extends SvelteComponentTyped<VirtualListProps> {}
}
