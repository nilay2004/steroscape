<script lang="ts">
	import { onMount } from 'svelte';
	import TimeGreeding from '../components/TimeGreeding.svelte';
	import Icon from '@iconify/svelte';
	import { fade, fly } from 'svelte/transition';
	import { fluidCb, updatePageIndex, userContext, viewPageIndex } from '../lib/store';
	import FilesInput from '../components/filesInput.svelte';
	let pageIndexChanged = false;
	let interval = undefined;
	let resetIndexChanges = () => {
		if (interval) clearTimeout(interval);
		interval = setTimeout(() => {
			pageIndexChanged = false;
		}, 1000);
	};
	$: pageIndexChanged, resetIndexChanges();
	let maxScrol = 50;
	let minScroll = 2;
	let index: number = 0;
	$: $viewPageIndex, (index = $viewPageIndex[1])
	let scrolls = minScroll;
	let m = scrolls;
	let maxPages = 3;
	const getIndex = (e: any) => {
		if (!(e.deltaY > 50 || e.deltaY < -50)) scrolls = maxScrol;
		else scrolls = minScroll;
		if (e.deltaY >= 0) {
			m--;
			if (m === 0) {
				index = index + 1;
				pageIndexChanged = true;
				m = scrolls;
			}
		}
		if (e.deltaY <= 0) {
			m--;
			if (m === 0) {
				index = index;
				index = index - 1;
				pageIndexChanged = true;
				m = scrolls;
			}
		}
		if (m === scrolls && index >= 0) {
			$fluidCb(2);
			index = index <= 0 ? 0 : index >= maxPages ? maxPages : index;
			updatePageIndex([$viewPageIndex[1], index]);
			window.localStorage.setItem('cur_page', `[${$viewPageIndex[1]}, ${index}]`);
		}
	};

	onMount(() => {
		document.addEventListener('wheel', (e) => {
			if (pageIndexChanged || e.shiftKey) return 0;
			getIndex(e);
		});
	});
</script>

<div class="super-cont">
	{#if $viewPageIndex[1] === 0}
		<div class="screen" in:fade={{ duration: 1000 }} out:fade={{ duration: 300 }}>
			<div class="h-txt scape">
				<div class="grad-tape">
					<p>
						<Icon icon="file-icons:cheetah3d" />
						StereoScape
					</p>
				</div>
			</div>
		</div>
	{/if}
	{#if $viewPageIndex[1] === 1}
		<div
			class="screen"
			in:fly={{ delay: 100, duration: 1000, y: $viewPageIndex[0] > $viewPageIndex[1] ? -500 : 500 }}
			out:fly={{ duration: 400, y: $viewPageIndex[0] > $viewPageIndex[1] ? 500 : -500 }}
		>
			<div class="screen2">
				<div class="time-greeding">
					<TimeGreeding />
				</div>
				<div class="flex-2">
					<div class="f20">
						<p class="h-title">Step into the Third Dimension,</p>
						<p class="h-title2">Welcome to StereoScape</p>
						<p>
							StereoScape is providing a place where every body can convert 2D images to 3D models.
							the converstion 2nd Dimension to 3rd Dimension the very intensive Deep Networks model
							is involve called NeRF (Neural Radiance Fields). the NeRF model take 2D set of images
							and create a 3D object from it.
						</p>
					</div>
					<div class="f21">
						<img src="/media/3d-gallery.jpg" alt="3d gallery" />
					</div>
				</div>
			</div>
		</div>
	{/if}
	{#if $viewPageIndex[1] === 2}
		<div
			class="screen"
			in:fly={{ delay: 100, duration: 1000, y: $viewPageIndex[0] > $viewPageIndex[1] ? -500 : 500 }}
			out:fly={{ duration: 400, y: $viewPageIndex[0] > $viewPageIndex[1] ? 500 : -500 }}
		>
			<div class="screen2">
				<div class="flex-2">
					<div class="f30">
						<p class="h-title">NeRF (Neural Radiance Fields)</p>
						<p>
							A NeRF (Neural Radiance Fields) model provides a way to represent and render 3D scenes
							and objects in a highly detailed and realistic way. it's a deep learning-based
							approach that learns to reconstruct the 3D scene from a set of 2D images.
						</p>
						<p class="h-title3">A NeRF model provides</p>
						<ul>
							<li>
								<b>3D reconstruction</b>
								<p>
									NeRF can reconstruct the 3D geometry, texture, and appearance of a scene or object
									from a set of 2D images.
								</p>
							</li>
							<li>
								<b>Novel View Synthesis</b>
								<p>
									NeRF can generate new views of the scene or object from any camera position,
									allowing, for virtual camera movements and 3D exploration.
								</p>
							</li>
							<li>
								<b>High-Res Image</b>
								<p>
									NeRF can generate high-resolution images (up to 4k) of the scene or object, with
									detailed textures and realistic lighting.
								</p>
							</li>
							<li>
								<b>Realistic Rendering</b>
								<p>
									NeRF can simulate various lighting conditions, shadows, and reflections, creating
									highly realistic renderings.
								</p>
							</li>
						</ul>
					</div>
					<div class="f21 nx3">
						<img src="/media/nerf_1.svg" class="x-c" alt="3d gallery" />
						<a target="_blank" href="/media/nerf_2.png">View image</a>
						<img src="/media/nerf_2.png" alt="3d gallery" />
						<a target="_blank" href="/media/nerf_2.png">View image</a>
					</div>
				</div>
			</div>
		</div>
	{/if}
	{#if $viewPageIndex[1] === 3}
		<div
			in:fly={{ delay: 100, duration: 1000, y: $viewPageIndex[0] > $viewPageIndex[1] ? -500 : 500 }}
			class="screen"
			out:fly={{ duration: 400, y: $viewPageIndex[0] > $viewPageIndex[1] ? 500 : -500 }}
		>
			<div class="screen2">
				<FilesInput />
			</div>
		</div>
	{/if}
</div>

<style lang="scss">
	.super-cont {
		position: absolute;
		width: 100vw;
		height: 100vh;
		overflow: hidden;
	}
	:root {
		--head-text-width: 720px;
	}
	.nx3 {
		width: 500px;
		text-align: center;
		& img {
			width: 100% !important;
			margin-top: 20px;
		}
		.x-c {
			filter: invert(1);
			width: 80%;
			margin-left: 15px;
		}
		& a {
			text-align: center;
			color: dodgerblue;
			text-decoration: underline;
			margin-bottom: 20px;
			display: block;
			width: 100px;
			margin: auto;
		}
	}
	.screen {
		width: 100%;
		height: 100vh;
		display: flex;
		align-items: center;
		position: absolute;
		justify-content: center;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
	}
	.screen2 {
		backdrop-filter: blur(18px);
		background: #1f1d1d30;
		padding: 20px;
		margin-top: 30px;
		border-radius: 12px;
		position: relative;
		& .h-title {
			font-size: 28px;
			font-weight: bold;
		}
		& .h-title2 {
			font-size: 58px;
			font-weight: bold;
		}
		& .flex-2 {
			margin-top: 10px;
			display: flex;
		}
		& .f20,
		& .f30 {
			margin-right: 10px;
			max-width: 650px;
		}
		& .f30 {
			max-width: 600px;
			font-size: 14px;
			line-height: 1.3;
			& .h-title3 {
				font-size: 20px;
				font-weight: bold;
			}
			& p {
				margin-bottom: 10px;
			}
			& b {
				margin-bottom: 4px;
				display: block;
			}
			& .btn-casual {
				margin-top: 18px;
			}
		}
		& .f21 {
			& img {
				width: 350px;
				border-radius: 8px;
			}
		}
	}

	:global(.grad-tape p svg) {
		color: #ff6692 !important;
	}
	.grad-tape {
		background: linear-gradient(90deg, #ff6692, #ff7c7c, #df59fa, #5ff3ff, #8eff8a, #ffc970);
		background-clip: text;
		text-transform: uppercase;
		color: transparent;
		-webkit-background-clip: text;
		-moz-background-clip: text;
		font-weight: 900;
	}
	:global(.scape p svg) {
		margin-top: 10px;
		margin-right: 12px;
	}
	.scape {
		width: 100%;
		align-items: center;
		justify-content: center;
		text-align: center;
		margin: auto;
		border-radius: 8px;
		padding: 3px;
		width: var(--head-text-width);
		backdrop-filter: blur(18px);
		& p {
			margin: auto;
			font-size: 90px !important;
			font-weight: 600;
			text-align: center;
			display: flex;
		}
	}
</style>
