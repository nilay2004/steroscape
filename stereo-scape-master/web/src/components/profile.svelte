<script lang="ts">
	import { updateMediaContext, userContext, userContextUpdate } from '../lib/store';
	// @ts-ignore
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import Icon from '@iconify/svelte';
	import { onMount } from 'svelte';
	import { Cookies, lazyLoad, life, numberFormat } from '../lib/globals';
	import axios from 'axios';

	let items = [];
	const setLazyLoad = () => {
		const lazyLoadList = document.querySelectorAll('video.lazy-load');
		lazyLoadList.forEach((element: HTMLImageElement | HTMLVideoElement) => {
			let src = element.getAttribute('data-src');
			lazyLoad(element, src);
		});
	};
	onMount(async () => {
		await getData(true);
	});
	const getData = async (getDates = false) => {
		if ($userContext.id) {
			await axios
				.get('/api/fetch/', {
					headers: {
						request: 'fetch_user_data'
					},
					params: { _id: $userContext.id }
				})
				.then((res) => {
					items = res.data;
					setTimeout(() => {
						setLazyLoad();
					}, 2000);
				})
				.catch((err) => {
					console.error(err);
				});
		}
	};
	const handleLogout = () => {
		Cookies.delete('user');
		userContextUpdate(false);
	};
</script>

<div class="profile">
	<div class="left">
		<div class="pic">
			<img src={$userContext.avatar} alt={$userContext.username} />
		</div>
		<span class="username"
			>@{$userContext.username}
			<br />
			{$userContext.passion != '' ? $userContext.passion : ''}
		</span>
		<span class="email">{$userContext.email}</span>
		<button on:click={handleLogout}>
			Logout <Icon icon="solar:logout-2-broken" />
		</button>
	</div>
	<div class="right">
		<h3>MY GALLERY</h3>
		<div class="">
			<div class="rows" id="scrollar">
				{#if items.length}
					{#each items as item}
						<div class="gal">
							{#if item.video}
								<video controls class="lazy-load" data-src={PUBLIC_BACKEND_URL + item.video}>
									<track kind="captions" />
								</video>
							{:else}
								<img class="place-img" src={PUBLIC_BACKEND_URL + '/media/' + item.media + '/1.jpg'} alt="" />
							{/if}
							<div class="galx">
								<span class="t">
									<li>{life(item.createAt).format('D MM YYYY')}</li>
									<li>
										{item.psnrs.pop()[1].toFixed(1)} psnr score on {numberFormat(
											item.psnrs.pop()[0]
										)}
										iterations
									</li></span
								>
								<button class="xy-b" on:click={() => updateMediaContext({...item, username: $userContext.username})}>
									Edit Pre-trained Model 
									<Icon icon="carbon:machine-learning-model" />
								</button>
								<!-- <a href="/datasetr">
									<Icon icon="ph:images-fill" />
									View images
								</a>
								<a href="/npz">
									<Icon icon="majesticons:data-line" />
									Download dataset file
								</a>
								<a href="/model">
									Download trained model</a
								> -->
								<span class="xz">Created on {life(item.createdAt).format('DD MM YYYY')}</span>
							</div>
						</div>
					{/each}
				{:else}
					<h1 style="margin-top: 40px; font-size: 22px; opacity: 0.5">NO ITEMS</h1>
				{/if}
			</div>
		</div>
	</div>
</div>

<style lang="scss">
	.rows {
		display: flex;
		max-width: 72vw;
		flex-wrap: nowrap;
		flex-direction: row;
		justify-content: flex-start;
		overflow-x: scroll;
	}

	:global(.galx a svg) {
		margin-right: 5px;
		font-size: 18px;
	}
	.xz {
		font-size: 12px;
		margin-top: 25px;
		color: rgba(255, 255, 255, 0.596);
	}
	.galx {
		display: flex;
		flex-direction: column;
		margin-top: 10px;
		width: 200px;
		& a {
			margin-top: 8px;
			font-size: 14px;
			display: flex;
			align-items: center;
			transition: 300ms;
			&:hover {
				color: rgb(255, 67, 154);
			}
		}
		& .t {
			margin-bottom: 20px;
			max-width: 200px;
		}
		& span {
			display: block;
		}
	}
	.gal {
		margin: 10px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-direction: column;
		text-align: center;
		background: #ffffff08;
		padding: 9px;
		border-radius: 20px;
		& video {
			width: 200px;
			height: 180px;
			object-fit: cover;
			border-radius: 13px;
		}
	}
	.right {
		border-left: 1px solid rgba(255, 255, 255, 0.076);
		min-width: 300px;
		min-height: 300px;
		padding-left: 15px;
		& h3 {
			font-size: 16px;
		}
	}
	:global(.profile .left button svg) {
		margin-left: 10px;
		font-size: 20px;
		display: block;
		background-color: blue($color: #000000);
	}
	.left {
		display: flex;
		align-items: center;
		justify-content: start;
		flex-direction: column;
		margin-right: 20px;
		& button {
			padding: 8px 20px;
			margin-top: 20px;
			background: rgba(0, 0, 0, 0.181);
			color: white;
			border: 1px solid rgba(255, 255, 255, 0.089);
			display: flex;
			justify-content: center;
			align-items: center;
			cursor: pointer;
			transition: 400ms;
			&:hover {
				background: black;
			}
		}

		& span.email {
			margin-top: 3px;
			margin-bottom: 3px;
			color: rgb(182, 182, 182);
		}
		& span.username {
			margin-top: 8px;
			color: rgb(229, 229, 229);
			font-size: 14px;
			text-align: center;
		}
		& .pic {
			width: 80px;
			height: 80px;
			border-radius: 50%;
			border: 2px solid rgba(255, 255, 255, 0.285);
			overflow: hidden;
		}
		& img {
			width: 100%;
			height: 100%;
			object-fit: cover;
		}
	}
	.profile {
		display: flex;
	}
.place-img{
	width: 100px;
	height: 100px;
	object-fit: cover;
	border-radius: 8px;
	margin-bottom: 10px;
}

.xy-b{
	height: 40px;
	background: rgb(7, 33, 112);
	border-radius: 6px;
	color: white;
	cursor: pointer;
	border:2px solid rgb(14, 67, 150);
	transition: 300ms;
	&:hover{
		background: rgb(15, 57, 183);
	}
}
</style>
