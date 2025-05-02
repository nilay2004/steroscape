<script lang="ts">
	import { slide } from 'svelte/transition';
	// @ts-ignore
	// import { updateSettings } from '$lib/store';
	import { editMediaContext, updateMediaContext } from '../lib/store';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import axios from 'axios';
	import { onMount } from 'svelte';

	let theta = -57;
	let phi = -29;
	let radius = 4.2;
	let visualImg:any = ''
	let loading = false;
	let prevImg:any = ''
	const getInteractiveVisualization = async () => {
		await axios.get(`${PUBLIC_BACKEND_URL}/get-visualz`, {params: {theta, phi, radius, media: $editMediaContext.media, prevImg}})
		.then(res => {
			res = res.data
			console.log(res)
			visualImg = res
			prevImg = res
		})
		.catch(err => {
			console.error(err)
		})
	}
	onMount(() => {
		getInteractiveVisualization()
	})
	const handleVidGen = async () => {
		const form = new FormData();
		form.append('media', $editMediaContext.media);
		form.append('user', $editMediaContext.user);
		form.append('_id', $editMediaContext._id);
		loading = true;
		await axios
			.post(`${PUBLIC_BACKEND_URL}/generate-video`, form)
			.then((res: any) => {
				res = res.data;
				loading = false;
				if (res.success) {
					updateMediaContext({ ...$editMediaContext, video: res.video });
				} else {
					console.error(res.message);
				}
			})
			.catch((err) => {
				console.error(err);
				loading = false;
			});
	};
</script>

<div class="modal" transition:slide>
	<div class="head">
		<h3>Edit pre-trained model of @{$editMediaContext.username}</h3>
		<button class="xuw" on:click={() => updateMediaContext(false)}>&times;</button>
	</div>
	<div class="container flex" id="setting_form">
		<div>
			<p>Media identification ({$editMediaContext.media})</p>
			<br />
			<p>360 video</p>
			{#if $editMediaContext.video}
				<video
					class="vid"
					autoplay
					muted
					loop
					controls
					src={PUBLIC_BACKEND_URL + $editMediaContext.video}
				>
					<track kind="captions" />
				</video>
			{:else}
				<button class="button" on:click={handleVidGen}>Click to generate 360 video</button>
			{/if}

			{#if loading}
				<span class="spinner"></span>
			{/if}
		</div>
		<div class="sec">
			<h2>Interactive Visualization</h2>
			<div class="aero">
				<div>
					<span>Theta: {theta} (rotation around Y-axis)</span>
					<input type="range" bind:value={theta} on:change={getInteractiveVisualization} name="theta" min={-90} step={1} max={90} id="" />
				</div>
				<div>
					<span>Phi: {phi} (rotation around X-axis)</span>
					<input type="range"  bind:value={phi} on:change={getInteractiveVisualization} name="phi" id="" min={-180} step={1} max={180} />
				</div>
				<div>
					<span>Radius: {radius} (translation along X, Y, and Z axes)</span>
					<input type="range"  bind:value={radius} on:change={getInteractiveVisualization} name="" id="" min={0} max={10} step={0.1} />
				</div>
				<div class="img">
					{#if visualImg != ''}
						<img src="{PUBLIC_BACKEND_URL + visualImg}" alt="vis">
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>

<style lang="scss">
	.aero{
	& .img{
				height: 180px;
				width: 200px;
				& img{
					width: 100%;
					height: 100%;
					object-fit: cover;

					border-radius: 8px;
				}
			}
		& div{

			display: flex;
			flex-direction: column;
			margin-bottom: 20px;
			& span{
				font-size: 13px;
			}
		}	
	}
	.sec{
		margin-left: 30px;
		padding-left: 15px;
		margin-top: 35px;
		border-left: 1px solid rgba(255, 255, 255, 0.136);
		& h2{
			margin-bottom: 10px;
			font-size: 20px;
		}
	}
	.flex {
		display: flex;
	}
	.vid {
		width: 200px;
		margin-top: 11px;
		border-radius: 8px;
	}
	.button {
		padding: 10px 20px;
		margin-top: 10px;
		font-size: 16px;
		background: rgb(11, 36, 120);
		color: white;
		border: 2px solid rgb(10, 78, 118);
		border-radius: 28px;
	}
	.head {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.container {
		margin-top: 30px;
	}
	.modal {
		position: fixed;
		z-index: 30;
		background: rgba(16, 16, 43, 0.704);
		left: 0;
		right: 0;
		backdrop-filter: blur(18px);
		top: 0;
		bottom: 0;
		max-width: 980px;
		max-height: 68%;
		margin: auto;
		border-radius: 8px;
		padding: 25px;
	}
</style>
