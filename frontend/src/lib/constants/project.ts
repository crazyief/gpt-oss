/**
 * Project constants
 *
 * Shared constants for project colors, icons, and configuration
 */

export const PROJECT_COLORS = [
	{ name: 'red', hex: '#EF4444', label: 'Red' },
	{ name: 'orange', hex: '#F97316', label: 'Orange' },
	{ name: 'yellow', hex: '#EAB308', label: 'Yellow' },
	{ name: 'green', hex: '#22C55E', label: 'Green' },
	{ name: 'blue', hex: '#3B82F6', label: 'Blue' },
	{ name: 'purple', hex: '#8B5CF6', label: 'Purple' },
	{ name: 'gray', hex: '#6B7280', label: 'Gray' },
	{ name: 'black', hex: '#1F2937', label: 'Black' }
] as const;

export const PROJECT_ICONS = [
	{ name: 'folder', emoji: '📁', label: 'Folder' },
	{ name: 'shield', emoji: '🛡️', label: 'Security' },
	{ name: 'document', emoji: '📄', label: 'Document' },
	{ name: 'chart', emoji: '📊', label: 'Analytics' },
	{ name: 'flask', emoji: '🧪', label: 'Research' },
	{ name: 'briefcase', emoji: '💼', label: 'Business' },
	{ name: 'target', emoji: '🎯', label: 'Goals' },
	{ name: 'star', emoji: '⭐', label: 'Favorites' }
] as const;

export type ProjectColorName = (typeof PROJECT_COLORS)[number]['name'];
export type ProjectIconName = (typeof PROJECT_ICONS)[number]['name'];

/**
 * Get color hex by name
 */
export function getColorHex(name: ProjectColorName): string {
	return PROJECT_COLORS.find((c) => c.name === name)?.hex || PROJECT_COLORS[4].hex; // Default blue
}

/**
 * Get icon emoji by name
 */
export function getIconEmoji(name: ProjectIconName): string {
	return PROJECT_ICONS.find((i) => i.name === name)?.emoji || PROJECT_ICONS[0].emoji; // Default folder
}
