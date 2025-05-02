<script>
	import { onMount } from 'svelte';
	export let classOnView = '';
	export let classOutView = 'fade-out';
	export let typingAnim= {
		animate: false,
		textContent: ''
	};
	export let Options  = {
		root: null,
		rootMargin: '0px',
		threshold: 0.45
	};
	let targetElement;
	let isInView = false;
	let intersectionObserver;
	let interval = undefined;
	const writeOnAnimation = (selector, content, speed = 40) => {
		let text = document.querySelector(selector);
		if(interval) clearInterval(interval)
		if (text) {
			text.innerText = '';
			let char = content.split('');
			let i = 0;
			interval = setInterval(() => {
				//@ts-ignore
				text.innerHTML += char[i] == ' ' ? '&nbsp;' : char[i];
				i++;
				if (char.length === i) clearInterval(interval);
			}, speed);
		}
	};
	function viewport(element) {
		if (intersectionObserver) return;
		intersectionObserver = new IntersectionObserver((entries) => {
			entries.forEach((entry) => {
				isInView = entry.isIntersecting;
				if (typingAnim.animate && typingAnim.selector)
					writeOnAnimation(typingAnim.selector, typingAnim.textContent);
				if(interval && !isInView) clearInterval(interval)
			});
		}, Options);
		intersectionObserver.observe(element);
		return {
			destroy() {
				intersectionObserver.unobserve(element);
			}
		};
	}
	onMount(() => {
		if (typingAnim.animate && typingAnim.selector) {
			targetElement = document.querySelector(typingAnim.selector);
		}
		viewport(targetElement);
	});
</script>

<div bind:this={targetElement} class={isInView ? classOnView : classOutView}>
	<slot />
</div>
