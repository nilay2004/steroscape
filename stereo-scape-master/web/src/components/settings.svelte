<script lang="ts">
	import { onMount } from 'svelte';
	import { slide } from 'svelte/transition';
	// @ts-ignore
	import { updateSettings } from '$lib/store';
	import { SettingsContext } from '../lib/store';

	let Settings: {
		image_width: number;
		image_height: number;
		modal_depth: number;
		modal_width: number;
		n_samples: number;
		n_iterations: number;
		use_colmap: number;
		isOpened: boolean;
	} = $SettingsContext;
	const handelInput = (event: any) => {
		let value = parseInt(event.target.value);
		let name = event.target.name;
		if (name === 'width') Settings.image_width = value;
		if (name === 'height') Settings.image_height = value;
		if (name === 'D') Settings.modal_depth = value;
		if (name === 'W') Settings.modal_width = value;
		if (name === 'N_samples') Settings.n_samples = value;
		if (name === 'N_iterations') Settings.n_iterations = value;
		if (name === 'use_colmap') Settings.use_colmap = value;
	};
	const handleSave = async (event: any) => {
		updateSettings({ ...Settings, isOpened: false });
		delete Settings.isOpened;
		localStorage.setItem('setting', JSON.stringify(Settings));
	};
	onMount(() => {
		const inputs = document.querySelectorAll('#setting_form input');
		inputs.forEach((input) => {
			input.addEventListener('change', handelInput);
		});
	});
</script>

<div class="modal" transition:slide>
	<div class="head">
		<h3>Settings</h3>
		<button class="xuw" on:click={() => updateSettings({ isOpened: false })}>&times;</button>
	</div>
	<div class="container" id="setting_form">
		<div class="group">
			<div>
				<div class="rough">
					<span>Width (px)</span>
					<input
						type="number"
						name="width"
						id="width"
						step="1"
						min="32"
						max="1024"
						value={Settings.image_width}
					/>
					<span>Height (px)</span>
					<input
						type="number"
						name="height"
						id="height"
						step="1"
						min="32"
						max="1024"
						value={Settings.image_height}
					/>
					<div class="info">
						<span class="iex"> &iexcl; </span>
						<span class="ms">
							width x height (set images width and height lower size can help to reduce training
							time but quality will effect)
						</span>
					</div>
				</div>
			</div>
		</div>
		<div class="group">
			<div>
				<p>Depth (number of layers keep 8 max).</p>
				<input
					type="number"
					name="D"
					id=""
					step="2"
					min="2"
					max="32"
					value={Settings.modal_depth}
				/>
			</div>
			<div style="margin-left: 25px">
				<p>Width (number of units/neurons in a layer max 256)</p>
				<input
					type="number"
					name="W"
					id=""
					step="1"
					min="8"
					max="1024"
					value={Settings.modal_width}
				/>
			</div>
			<div class="info" style="margin-top: -5px">
				<span class="iex"> &iexcl; </span>
				<span class="ms">
					Set D (depth) and W (width) of NeRF model network. Depth is number of layers (for NeRF 8
					is best) and Width is number of neurons (256 units) in each layer. D and W determine the
					capacity and complexity of the NN. increasing D or W can improve the model's ability to
					fit complex data, but also increase the risk of overfitting.
				</span>
			</div>
		</div>
		<div class="group">
			<div>
				<p>Number of samples.</p>
				<input
					type="number"
					name="N_samples"
					id=""
					step="1"
					min="16"
					max="1024"
					value={Settings.n_samples}
				/>
			</div>
			<div style="margin-left: 75px;">
				<p>Number of Iterations</p>
				<input
					type="number"
					name="N_iterations"
					id=""
					step="1"
					min="10"
					max="1000"
					value={Settings.n_iterations}
				/>
			</div>
			<div class="info" style="margin-top: -5px">
				<span class="iex"> &iexcl; </span>
				<span class="ms">
					<b>Number of samples:</b> less images and a high number of samples can overfit model. so
					set with caution.
					<br>
					<b> Number of Iterations: </b>
					More iteration can give max quality but slow speed. set 1000 for best result 250 for normal
					quality
				</span>
			</div>
		</div>
		<div class="group center">
			<input
				type="checkbox"
				name="use_colmap"
				id="use_colmap"
				checked={Settings.use_colmap ? true : false}
			/>
			<label for="use_colmap">Use colmap to extract cameras parameters (good but takes time).</label
			>
		</div>
		<div class="x92">
			<button class="save-btn" on:click={handleSave}>Save Setting</button>
		</div>
	</div>
</div>

<style lang="scss">
	.center {
		align-items: center;
		& label {
			margin-top: 8px;
			font-size: 14px;
		}
	}
	.group input[type='checkbox'] {
		width: 20px !important;
		height: 20px !important;
		margin-right: 10px;
	}
	.x92 {
		display: flex;
		align-items: end;
		justify-content: right;
	}
	.save-btn {
		width: 150px;
		border-radius: 28px;
		background: rgb(255, 255, 255);
		border: 2px solid rgba(255, 255, 255, 0.608);
		height: 40px;
		font-family: inherit;
		margin-top: 20px;
		margin-bottom: 10px;
		cursor: pointer;
		transition: 300ms;
		&:hover {
			background: none;
			color: white;
		}
	}
	div.info {
		margin-left: 20px;
		& .iex {
			background: rgb(36, 36, 90);
			border: 1px solid rgba(255, 255, 255, 0.096);
			width: 25px;
			height: 25px;
			border-radius: 50%;
			display: flex;
			align-items: center;
			justify-content: center;
			font-weight: bold;
			text-align: center;
			cursor: pointer;
			z-index: -1;
			position: relative;
		}

		& .ms {
			position: absolute;
			z-index: 9;
			padding: 8px 5px;
			border-radius: 4px;
			font-size: 14px;
			line-height: 1.4;
			color: #dfdfdf;
			width: 300px;
			margin-top: 4px;
			background: rgb(29, 28, 78);
			border: 1px solid rgba(245, 245, 245, 0.105);
			visibility: hidden;
			opacity: 0;
			transition: 300ms ease-out;
		}
		position: relative;
		z-index: 1000;

		&:hover > .ms {
			visibility: visible;
			opacity: 1;
		}
	}
	.head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		& button {
		}
	}
	.container {
		margin-top: 30px;
		& .group {
			display: flex;
			justify-content: left;
			margin-bottom: 15px;
			margin-top: 10px;
			& div.rough {
				display: flex;
				flex-direction: row;
				align-items: end;
				& #width {
					margin-right: 50px;
				}
				& span {
					margin-right: 13px;
				}
				& input {
					width: 60px;
				}
			}
			& p {
				font-size: 14px;
			}
			& input {
				margin-top: 8px;
				font-size: 16px;
				outline: none;
				width: 150px;
				height: 30px;
				padding: 0 10px;
				background: none;
				color: white;
				border: none;
				border-bottom: 1px solid rgba(255, 255, 255, 0.614);
			}
		}
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
