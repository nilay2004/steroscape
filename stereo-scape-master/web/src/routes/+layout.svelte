<script lang="ts">
	import Header from '../components/Header.svelte';
	import ThreeScene from '../threeScenes/threeScene.svelte';
	import '../styles/main.scss';
	import { onMount } from 'svelte';
	import { Cookies } from '../lib/globals';
	import {
		viewPageIndex,
		SettingsContext,
		updatePageIndex,
		userContextUpdate,
		updateSettings,
		editMediaContext
	} from '../lib/store';
	import Settings from '../components/settings.svelte';
	import EditMedia from '../components/editMedia.svelte';

	let fluidLights: any = false;
	let buttonIndex = [0, 0];
	$: $viewPageIndex, (buttonIndex = $viewPageIndex);

	let labels = [
		'Stereo Scape',
		'Welcome!',
		'What is NeRF?',
		'Upload your images'
	];
	onMount(() => {
		const cur_page = window.localStorage.getItem('cur_page');
		if (cur_page) updatePageIndex(JSON.parse(cur_page));
		const settings = localStorage.getItem('setting');
		if (settings) updateSettings(JSON.parse(settings));
		const f = JSON.parse(Cookies.get('fluid_lights'));
		if (f === null) fluidLights = true;
		else fluidLights = f;
		let user: any = Cookies.get('user');
		if (user) {
			user = JSON.parse(user);
			userContextUpdate(user);
		}
	});
	const toggleFluid = () => {
		fluidLights = !fluidLights;
		Cookies.set('fluid_lights', fluidLights, { expires: 365 });
	};
	const handlePage = (i: number) => {
		updatePageIndex([$viewPageIndex[1], i]);
		window.localStorage.setItem('cur_page', `[${$viewPageIndex[1]}, ${i}]`);
	};
</script>

{#if fluidLights}
	<ThreeScene />
{/if}
<div class="wrapper" id="boundary">
	{#if $editMediaContext}
		<EditMedia />
	{/if}
	{#if $SettingsContext.isOpened}
		<Settings />
	{/if}
	<div class="boundary">
		<Header fluidToggle={toggleFluid} fluid={fluidLights} />
		<main>
			<slot />
			<div class="left-button-list">
				{#each labels as label, i}
					<button
						on:click={() => handlePage(i)}
						class={buttonIndex[1] === i ? 'tag-uper active' : 'tag-uper'}
					>
						<span class="tag-label">{label}</span>
					</button>
				{/each}
			</div>
		</main>
	</div>
</div>

<style>
	.tag-uper {
		position: relative;
		&:hover {
			& .tag-label {
				visibility: visible;
				opacity: 1;
			}
		}
	}
	.tag-label {
		background: #0f202f;
		border: 1px solid #ffffff17;
		position: relative;
		position: absolute;
		right: 24px;
		top: -5px;
		width: max-content;
		display: block;
		padding: 3px 7px;
		border-radius: 2px;
		padding-right: 9px;
		color: rgba(255, 255, 255, 0.843);
		font-size: 12px;
		visibility: hidden;
		opacity: 0;
		transition: 300ms;
		&:after {
			content: '';
			width: 7px;
			height: 7px;
			background: #0f202f;
			border-top: 1px solid #ffffff17;
			border-right: 1px solid #ffffff17;
			position: absolute;
			right: -5px;
			transform: rotate(45deg);
			top: 6px;
			bottom: 0;
		}
	}
	.left-button-list {
		display: flex;
		position: fixed;
		right: 20px;
		align-items: center;
		justify-content: center;
		top: 0;
		bottom: 0;
		flex-direction: column;
		& button {
			border-radius: 50%;
			width: 16px;
			height: 16px;
			border: 2px solid #ffffff3b;
			text-align: center;
			padding: 0;
			cursor: pointer;
			background: #fdfdfd4f;
			margin: 3px 0;
			transition: 300ms;
			&:hover {
				background: #ffffffc8;
			}
			&.active {
				background: #ffffffc8;
			}
		}
	}
	.boundary {
		width: 100vw;
		height: 100vh;
		overflow: hidden;
	}
</style>
