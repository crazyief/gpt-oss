/**
 * Type guard utilities
 *
 * Runtime type checking functions for safer type narrowing.
 * Reduces need for 'any' types and type assertions.
 */

/**
 * Check if value is a non-null object
 *
 * @param value - Value to check
 * @returns true if value is an object (not null, not array)
 *
 * @example
 * if (isObject(data)) {
 *   // TypeScript knows data is Record<string, unknown>
 *   console.log(data.someProperty);
 * }
 */
export function isObject(value: unknown): value is Record<string, unknown> {
	return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Check if value is a string
 *
 * @param value - Value to check
 * @returns true if value is a string
 *
 * @example
 * if (isString(input)) {
 *   // TypeScript knows input is string
 *   console.log(input.toUpperCase());
 * }
 */
export function isString(value: unknown): value is string {
	return typeof value === 'string';
}

/**
 * Check if value is a number
 *
 * @param value - Value to check
 * @returns true if value is a finite number
 *
 * @example
 * if (isNumber(id)) {
 *   // TypeScript knows id is number
 *   const doubled = id * 2;
 * }
 */
export function isNumber(value: unknown): value is number {
	return typeof value === 'number' && !isNaN(value) && isFinite(value);
}

/**
 * Check if value is an Error object
 *
 * @param value - Value to check
 * @returns true if value is an Error instance
 *
 * @example
 * if (isError(caught)) {
 *   // TypeScript knows caught is Error
 *   console.error(caught.message, caught.stack);
 * }
 */
export function isError(value: unknown): value is Error {
	return value instanceof Error;
}

/**
 * Check if object has a specific property
 *
 * @param obj - Object to check
 * @param key - Property key
 * @returns true if object has the property
 *
 * @example
 * if (hasProperty(data, 'id')) {
 *   // TypeScript knows data has 'id' property
 *   console.log(data.id);
 * }
 */
export function hasProperty<K extends string>(
	obj: unknown,
	key: K
): obj is Record<K, unknown> {
	return isObject(obj) && key in obj;
}

/**
 * Assert value is defined (not null or undefined)
 *
 * @param value - Value to check
 * @param message - Optional error message
 * @throws Error if value is null or undefined
 * @returns value (TypeScript narrows type to non-nullable)
 *
 * @example
 * const element = document.getElementById('app');
 * assertDefined(element, 'App element not found');
 * // TypeScript knows element is HTMLElement (not null)
 * element.classList.add('active');
 */
export function assertDefined<T>(
	value: T | null | undefined,
	message: string = 'Value is null or undefined'
): asserts value is T {
	if (value === null || value === undefined) {
		throw new Error(message);
	}
}

/**
 * Safely extract error message from unknown error type
 *
 * Handles Error objects, strings, objects with message property, and unknown types.
 *
 * @param error - Unknown error value from catch block
 * @returns User-friendly error message
 *
 * @example
 * try {
 *   await riskyOperation();
 * } catch (err) {
 *   const message = getErrorMessage(err);
 *   toast.error(message);
 * }
 */
export function getErrorMessage(error: unknown): string {
	// Error object
	if (isError(error)) {
		return error.message;
	}

	// String error
	if (isString(error)) {
		return error;
	}

	// Object with message property
	if (hasProperty(error, 'message') && isString(error.message)) {
		return error.message;
	}

	// Object with detail property (FastAPI format)
	if (hasProperty(error, 'detail') && isString(error.detail)) {
		return error.detail;
	}

	// Unknown error type
	return 'An unexpected error occurred';
}
