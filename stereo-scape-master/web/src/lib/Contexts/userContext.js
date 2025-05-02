import { writable } from 'svelte/store';

export const userContext = writable(false);

export const updateUserContext = (user) => {
    userContext.update(() => user);
}; 