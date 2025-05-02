<script lang="ts">
	//@ts-ignore
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import Icon from '@iconify/svelte';
	import {scale, slide, fade} from 'svelte/transition'
	import axios from 'axios';
	//@ts-ignore
	import { numberFormat, life } from '../lib/globals';
	import { onMount } from 'svelte';
	import PnrsGraph from './pnrs-graph.svelte';
	import { updateMediaContext } from '../lib/store';
	let data = [];
	let loading = false;
	let dataloaded = false;
	let section_class = '';
	let sliderValue = 0;
	let itemsLimit = 3;
	let currentValue = 1;
	let message: {message:string, variant:string} | boolean  = false;
	let tooltip = undefined;
	let modalData:{isOpened:boolean, title?:string, video?:string} = { isOpened: false};
	const getData = async (limit: number = 5, skip: number = 0, total_count = false) => {
		loading = true;
		await axios
			.get('/api/fetch', {
				params: { skip, limit, total_count },
				headers: { request: 'fetch_users_data' }
			})
			.then((res) => {
				const r: any = res.data;
				loading = false;
				if (total_count) sliderValue = Math.ceil(r.total / itemsLimit);
				dataloaded = true;
				handleClassTransition(() => {
					data = r.data;
				});
			})
			.catch((err) => console.error(err));
	};
	onMount(() => {
		tooltip = document.getElementById('tooltip');
		setTimeout(() => {
			getData(3, 0, true);
		}, 1000);
	});
	const handleClassTransition = (cb: () => void) => {
		if (section_class === 'open') section_class = 'close';
		setTimeout(() => {
			section_class = 'open';
			cb();
		}, 500);
	};
	const handleSlider = (e: any) => {
		let rect = e.target.getBoundingClientRect();
		const x = e.clientY - rect.top;
		let percent = (x / rect.height) * 100;
		let value = (percent / 100) * e.target.max + e.target.min;
		if (value <= sliderValue && value > 0) {
			if (percent <= 100) tooltip.style.top = `${percent}%`;
			tooltip.innerText = Math.floor(value) + 1;
		}
	};
	const handleToolTip = () => {
		tooltip.classList.toggle('active');
	};
	const handleMouseDown = (e: any, action) => {
		if (action) e.target.classList.add('active');
		else e.target.classList.remove('active');
	};
	const handleInputRange = async () => {
		await getData(itemsLimit, (currentValue - 1) * itemsLimit);
	};
</script>

{#if modalData.isOpened}
	<div class="modal" out:scale={{start: 0.2}} in:scale={{start:1.5}}>
		<div class="flex">
			<span>{modalData.title}</span>
			<button class="xuw" on:click={() => (modalData.isOpened = false)}>&times;</button>
		</div>
		<div>
			<video src={PUBLIC_BACKEND_URL + modalData.video} controls loop muted>
				<track kind="captions" />
			</video>
			<a href="#" download={PUBLIC_BACKEND_URL + modalData.video}>Download</a>
		</div>
	</div>
{/if}
<div class="container">
	<div class="left">
		<h3>Move slider to see more items {sliderValue ? `${currentValue} of ${sliderValue}` : ''}</h3>
		<input
			type="range"
			on:mousemove={handleSlider}
			on:mouseenter={handleToolTip}
			on:mouseleave={handleToolTip}
			on:mousedown={(e) => handleMouseDown(e, 1)}
			on:mouseup={(e) => handleMouseDown(e, 0)}
			on:change={handleInputRange}
			name="pagin"
			id="pagin"
			bind:value={currentValue}
			max={sliderValue}
			min={1}
		/>
		<span class="tooltip" id="tooltip">{currentValue}</span>
	</div>
	<div class="gallery">
		{#if data.length}
			{#each data as item}
				<section class={section_class} role="" aria-labelledby="dropzone-label">
					<div class="top">
						<div class="profile">
							<img src={item.user.avatar} alt={item.user.username} />
							<h2>{item.user.fullname}</h2>
							<h3>@{item.user.username}</h3>
							<p class="ct">{life(item.createdAt).from()}</p>
						</div>
						<div class="project">
							<div class="xero">
								<span class="db">{item.psnrs.pop()[1].toFixed(1)}dB</span>
								on
								<span class="iter">{numberFormat(item.psnrs.pop()[0])} Iterations </span>
							</div>
							<div class="pnrs-graph">
								<PnrsGraph
									config={{
										height: 77,
										width: 215,
										title: false,
										xAxis: false,
										yAxis: false,
										background: '#1e082f00',
										line_color: '#0080ff'
									}}
									seriesData={item.psnrs}
								/>
							</div>
							<button
								class="vid-p"
								on:click={() =>
									(modalData = {
										isOpened: true,
										title: item.user.username + ' video',
										video: item.video
									})}
							>
								<Icon icon="material-symbols-light:not-started-outline" style="color: #00ccff" />
								video
							</button>
							<button 
								class="vid-p"
							 on:click={() => updateMediaContext({...item, username: item.user.username})}>
									Edit Model 
									<Icon icon="carbon:machine-learning-model" />
								</button>

						</div>
					</div>
					<div class="bottom">
						<button>{life(item.createdAt).format('DD MM YYYY')}</button>
					</div>
				</section>
			{/each}
		{:else}
			{#each Array(3).fill(0) as item}
				<section class="onLoad {dataloaded ? 'close' : ''}">
					<div>
						<span class="img"></span>
						<span></span>
						<span></span>
					</div>
					<div>
						<span></span>
						<span class="_xj"></span>
						<span></span>
					</div>
					<div>
						<span class="graph"></span>
						<span class="_xj"></span>
					</div>
				</section>
			{/each}
		{/if}
	</div>
</div>

<style lang="scss">
	.modal {
		& .flex {
			display: flex;
			justify-content: space-between;
			align-items: center;
			margin: 15px 20px;
			& span {
				font-size: 18px;
			}
		}
		& video {
			display: block;
			min-width: 131px;
			border-radius: 6px;
			margin: 10px auto;
		}
		& a {
			background: rgb(255, 0, 89);
			margin: auto;
			display: block;
			text-align: center;
			width: max-content;
			padding: 6px 8px;
			margin-bottom: 15px;
			font-weight: 500;
			border-radius: 4px;
			font-size: 14px;
		}

		position: absolute;
		width: 450px;
		height: max-content;
		background: rgb(7, 12, 12);
		z-index: 3;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		margin: auto;
		border-radius: 12px;
		border: 1px solid rgba(173, 216, 230, 0.062);
	}
	:global(.container .left input[type='range']) {
		&.active {
			cursor: grabbing;
		}
	}
	.container {
		display: flex;
		flex-wrap: nowrap;
		align-items: center;
		& .left {
			max-height: 400px;
			margin-right: 80px;
			position: relative;
			& h3 {
				position: absolute;
				left: -30px;
				color: rgb(170, 170, 170);
				top: 0;
				font-size: 18px;
				font-weight: 600;
				bottom: 0;
				writing-mode: vertical-lr;
			}
			& .tooltip {
				text-align: center;
				display: inline-block;
				width: 25px;
				background: #dfdfdf;
				border-radius: 4px;
				padding: 4px 12px;
				position: absolute;
				color: black;
				right: -53px;
				opacity: 0;
				transition: opacity 400ms;
				&.active {
					opacity: 1;
				}
				&:after {
					content: '';
					width: 8px;
					height: 8px;
					background: #dfdfdf;
					transform: rotate(45deg);
					position: absolute;
					left: -4px;
					top: 0;
					bottom: 0;
					margin: auto;
				}
			}
			& input[type='range'] {
				height: 100%;
				// -webkit-appearance: slider-vertical;
				writing-mode: vertical-lr;
				cursor: grab;
			}
		}
	}
	.onLoad {
		margin: 5px;
		width: 200px;
		padding: 10px 10px;
		background: #0f082f85;
		backdrop-filter: blur(18px);
		border-radius: 12px;
		border: 1px solid #ffffff24;
		& div {
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
			margin: auto;
			margin-bottom: 10px;
			&:nth-child(1) {
				width: 140px;
			}
		}
		& span {
			background: rgba(255, 255, 255, 0.112);
			height: 15px;
			border-radius: 8px;
			width: 100%;
			display: block;
			margin: 3px 0;
			position: relative;
			overflow: hidden;
			&.graph {
				height: 90px;
			}
			&._xj {
				width: 40px;
				height: 10px;
			}
			&.img {
				width: 70px;
				height: 70px;
				border-radius: 50%;
				margin-bottom: 10px;
			}
			&:after {
				content: '';
				width: 100%;
				height: 100%;
				position: absolute;
				background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.074), transparent);
				animation: lox 1s linear forwards infinite;
				@keyframes lox {
					0% {
						transform: translateX(-100%);
					}
					100% {
						transform: translateX(100%);
					}
				}
			}
		}
	}
	:global(.gallery section) {
		&.open {
			transform: rotateY(33deg) translate(450px, -105px);
			opacity: 0;
			animation: secOpen 400ms linear 1 forwards;
		}
		&.close {
			transition: 400ms;
			opacity: 1;
			animation: secClose 400ms ease-in 1 forwards;
		}
		@keyframes secClose {
			100% {
				opacity: 0;
				transform: rotateY(-60deg) translate(-63px, 141px);
			}
		}
		@keyframes secOpen {
			100% {
				opacity: 1;
				transform: rotateY(0deg) translate(0px, 0px);
			}
		}
	}
	:global(.vid-p svg) {
		font-size: 28px;
		margin-right: 5px;
		transition: 300ms;
	}
	:global(.vid-p:hover > svg) {
		color: rgb(255, 86, 199) !important;
	}
	.vid-p {
		margin: 5px auto;
		display: flex;
		align-items: center;
		justify-content: center;
		background: none;
		color: white;
		cursor: pointer;
		border: none;
		font-size: 14px;
	}
	.bottom {
		position: relative;
		& button {
			position: absolute;
			bottom: -30px;
			left: 0;
			right: 0;
			width: max-content;
			margin: auto;
			background: none;
			color: white;
			border: none;
		}
	}
	.ct {
		font-size: 11px;
		margin: 4px auto 0 0;
		color: rgba(248, 248, 248, 0.565);
		font-weight: 300;
	}
	.pnrs-graph {
		margin: 5px;
	}
	.xero {
		text-align: center;
		& .db,
		& .iter {
			display: block;
			font-size: 20px;
			font-weight: bold;
			color: #b9b9b9;
		}
	}
	.pnrs-graph {
		height: 100px;
	}
	.profile {
		text-align: center;
		margin: 10px 0;
		& h2 {
			font-size: 16px;
		}
		& h3 {
			font-size: 14px;
		}
		& h3,
		h2 {
			color: rgba(255, 255, 255, 0.724);
			font-weight: 300;
		}
		& img {
			width: 70px;
			height: 70px;
			border-radius: 50%;
			object-fit: cover;
			border: 2px solid #ffffff29;
		}
	}
	.gallery {
		display: flex;
		perspective: 1000px;
		width: 725px;
		justify-content: center;
		& section {
			& .top {
				overflow: hidden;
				margin: 2px;
			}

			background: #0f082f43;
			border: 1px solid #ffffff24;
			backdrop-filter: blur(18px);
			border-radius: 12px;
			margin: 5px;
			width: 230px;
		}
	}
</style>
