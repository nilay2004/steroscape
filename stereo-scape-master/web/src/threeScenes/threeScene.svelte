<script>
	import { onDestroy, onMount } from 'svelte';
	import { __init__ } from './script';
	import { updateFluidCb } from '../lib/store';
	let cb = undefined;
	let interval = undefined
	onMount(() => {
		cb = __init__(document.getElementById('canvas'));
		updateFluidCb(cb);
		interval = setInterval(() => {
			cb(2)	
		}, 2000);
	});
	onDestroy(() => {
		cb = undefined;
		if(interval) clearInterval(interval)
		updateFluidCb(() => {});
	});
</script>

<div>
	<canvas id="canvas"></canvas>
</div>

<style>
	div {
		position: fixed;
		top: 0;
		bottom: 0;
		left: 0;
		right: 0;
		width: 100%;
		z-index: -1;
	}
	#canvas {
		display: block;
		margin: 0 auto;
		width: 100vw;
		height: 100vh;
	}
</style>
