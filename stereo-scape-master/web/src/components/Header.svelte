<script lang="ts">
	import Icon from '@iconify/svelte';
	import { viewPageIndex, updateSettings, userContext, SettingsContext } from '../lib/store';
	export let fluidToggle;
	export let fluid;
</script>

<header class={$viewPageIndex[1] > 0 ? 'active' : ''}>
	<nav>
		<ul>
			<li>
				<h2>
					<Icon icon="file-icons:cheetah3d" />
					StereoScape
				</h2>
			</li>
		</ul>
		<ul>
			<li class="fluid">
				<span>Fluid Lights</span>
				<button on:click={fluidToggle} class={fluid ? 'active' : ''}> </button>
			</li>
			<li>
				<a href="/">
					<Icon icon="iconamoon:home" />
				</a>
			</li>
			<li>
				<button
					class="setting {$SettingsContext.isOpened ? 'active' : ''}"
					on:click={() => updateSettings({ isOpened: !$SettingsContext.isOpened })}
				>
					<Icon icon="line-md:cog-loop" />
				</button>
			</li>
		</ul>
	</nav>
</header>

<style>
	.setting {
		background: none;
		border: none;
		color: white;
		font-size: 26px;
		padding: 0;
		cursor: pointer;
		&.active,
		&:hover {
			color: #ffa300;
		}
	}
	h2 {
		font-weight: bold;
		font-size: 23px;
		display: flex;
		align-items: center;
		transition: 300ms;
		& svg {
			transition: 300ms;
			margin-right: 10px;
			width: 35px;
			height: 35px;
		}
	}
	nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin: 0 20px;
		height: 100%;
	}
	ul {
		display: flex;
		align-items: center;
	}
	li {
		margin: 0 5px;
	}
	a {
		margin: 0 10px;
		&:hover {
			color: #ffa300;
		}
		& img {
			width: 36px;
			height: 36px;
			border-radius: 50%;
			object-fit: cover;
			border: 2px solid #ffffff4a;
		}
	}
	:global(header nav a svg) {
		transition: 300ms;
		width: 25px;
		height: 25px;
	}
	.fluid {
		display: flex;
		align-items: center;
		justify-content: center;
		& span {
			font-size: 14px;
			font-weight: 300;
			font-family: 'JetBrainsMono Nerd Font', consolas;
		}
		& button {
			cursor: pointer;
			width: 35px;
			height: 20px;
			border-radius: 28px;
			margin: 0 5px;
			border: 2px solid transparent;
			border-color: rgba(255, 255, 255, 0.678);
			background: rgba(22, 0, 0, 0);
			position: relative;
			transition: 300ms;
			&:after {
				transition: 300ms;
				content: '';
				width: 14px;
				height: 14px;
				border-radius: 50%;

				background: radial-gradient(rgb(164, 164, 164), rgb(181, 181, 182));
				position: absolute;
				left: 0px;
				top: 0;
				bottom: 0;
				margin: 1px;

				margin-left: 16px;
			}
			&.active {
				border-color: rgba(0, 162, 250, 0.788);
				&:after {
					background: radial-gradient(rgb(31, 53, 252), rgb(58, 183, 255));
					margin-left: 1px;
				}
			}
		}
	}
	header {
		position: fixed;
		width: 100%;
		height: 90px;
		z-index: 3;
		transition: 300ms;
		&.active {
			/* background: rgba(255, 255, 255, 0.135); */

			backdrop-filter: blur(18px);
			height: 50px;
			& h2 {
				font-size: 18px;
				& svg {
					width: 28px;
					height: 28px;
				}
			}
		}
	}
	:global(header.active nav a svg, header.active nav button svg) {
		width: 20px;
		height: 20px;
	}
</style>
