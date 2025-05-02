<script>
    import Profile from '../../components/profile.svelte';
    import { userContext } from '../../lib/store';
    import { onMount } from 'svelte';
    
    let isLoggedIn = false;
    
    onMount(() => {
        isLoggedIn = $userContext && $userContext.id;
        if (!isLoggedIn) {
            window.location.href = '/login';
        }
    });
</script>

<svelte:head>
    <title>My Profile - StereoScape</title>
</svelte:head>

{#if isLoggedIn}
    <Profile />
{:else}
    <div class="loading">Loading profile...</div>
{/if}

<style>
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 300px;
        font-size: 18px;
        color: #888;
    }
</style> 