<script lang="ts">
	import { WEBSITE_NAME } from '../lib/config';
	import axios from 'axios';
	import Icon from '@iconify/svelte';
	import {userContextUpdate} from '../lib/store'
	import { slide } from 'svelte/transition';
	import { Cookies, createForm } from '../lib/globals';
	let loading = false;
	let interval = undefined;
	let message: any | { message: string; variant: string } = false;
	const filterUsername: (text: string) => string = (text) => text.replace(/[^a-zA-Z_]/g, '');
	const dataset = {
		fullname: '',
		username: '',
		email: '',
		passion: '',
		password: '',
		rePassword: '',
		avatar: undefined
	};
	const showMessage = (
		id: string,
		body: { text: string; variant: string; cssClass?: string },
		focus = true
	) => {
		const target = document.getElementById(id);
		if (focus) target.focus();
		const isExist = target.parentElement.querySelector(`.message`);
		if (isExist) {
			isExist.innerHTML = body.text;
			isExist.classList.remove('alert');
			isExist.classList.remove('success');
			isExist.classList.remove('danger');
			isExist.classList.add(body.variant);
			return 0;
		}
		target.style.borderBottomColor = 'orangered';
		const new_ = document.createElement('span');
		new_.innerText = body.text;
		new_.classList.add('message');
		new_.classList.add('inline');
		new_.classList.add(body.variant);
		if (body.cssClass) new_.classList.add(body.cssClass);
		target.parentElement.appendChild(new_);
	};
	const removeMessage: (input_id: string | Array<Array<string>>, span_id?: string) => void = (
		input_id,
		span_id
	) => {
		const rem = (id: string, span: string) => {
			try {
				const p: HTMLElement = document.querySelector(id);
				p.style.borderBottomColor = '#ffffff21';
				let k = p.parentElement.querySelector(span);
				k.remove();
			} catch (e) {}
		};
		if (typeof input_id === 'string') rem(input_id, span_id);
		else for (let i of input_id) rem(i[0], i[1]);
	};
	const checkUsername = async (event: string | Event) => {
		let username = '';
		if (typeof event !== 'string') username = (event.target as HTMLInputElement).value;
		if (filterUsername(username) !== username) {
			showMessage('username', {
				text: 'Only text and underscore is allowed! ❌',
				variant: 'danger'
			});
			dataset.username = '';
			return 0;
		}
		if (interval) clearTimeout(interval);
		interval = setTimeout(async () => {
			showMessage(
				'username',
				{
					text: 'checking username...',
					variant: 'alert',
					cssClass: 'spinner'
				},
				false
			);
			await axios
				.get('/api/_users/', { params: { username } })
				.then((response) => {
					removeMessage('#username', '.message.alert.spinner');
					if (response.data.user === 0) dataset.username = username;
					else dataset.username = '';
					showMessage(
						'username',
						{
							text: response.data.user === 0 ? 'username available ✔' : 'username not available',
							variant: response.data.user === 0 ? 'success' : 'alert'
						},
						false
					);
				})
				.catch((error) => {
					message = { message: error, variant: 'danger' };
					console.error(error);
				});
		}, 800);
	};
	const handelForm = async (event: SubmitEvent) => {
		if(loading) return 0
		removeMessage([
			['#email', '.message'],
			['#fullname', '.message'],
			['#password', '.message'],
			['#re-pass', '.message']
		]);
		let username = event.target['username'].value;
		let fullname = event.target['fullname'].value;
		let email = event.target['email'].value;
		let passion = event.target['passion'].value;
		let password = event.target['password'].value;
		let repassword = event.target['re-pass'].value;
		let avatar = event.target['avatar'].files[0];
		if (fullname === '' || fullname.length < 4) {
			showMessage('fullname', { text: 'Please enter your fullname!', variant: 'alert' });
			return 0;
		}
		if (username !== dataset.username) checkUsername(username);
		if (email === '') {
			showMessage('email', { text: 'Please enter email address!', variant: 'alert' });
			return 0;
		}
		if (password === '' || password.length < 8) {
			showMessage('password', { text: 'Enter password more than 8 chars.', variant: 'danger' });
			return 0;
		}
		if (password !== repassword) {
			showMessage('re-pass', { text: 'Your entered password is not matching!', variant: 'danger' });
			return 0;
		}
		dataset.email = email;
		dataset.fullname = fullname;
		dataset.passion = passion;
		dataset.password = password;
		if (avatar) dataset.avatar = avatar;
		await save_form();
	};
	const save_form = async () => {
		loading = true
		const form = createForm(dataset);
		message = false;
		console.log('sending...req')
		await axios
			.post('/api/_users/', form, {
				headers: {
					request: 'sign_up'
				}
			})
			.then((res: any) => {
				loading = false;
				res = res.data;
				console.log('res => ', res)
				if (res.success === 0) message = { message: res.message, variant: 'danger' };
				if (res.success === 1) {
					message = { message: res.message, variant: 'success' };
					Cookies.set('user', JSON.stringify(res.user), {expires: 365});
					userContextUpdate(res.user)
				}
			})
			.catch((error) => {
				loading = false;

				console.log('res => ', error)
				if (error.response.status === 422) {
					console.error(error.response.data.message);
					message = { message: error.response.data.message, variant: 'danger' };
				} else console.error(error.message);
			});
	};
	const handleProfile = (ev: Event) => {
		const img = (ev.target as HTMLInputElement).files[0];
		const reader = new FileReader();
		reader.onload = (event) => {
			const contents: any = event.target.result;
			const viewer: any = document.getElementById('image-view');
			const img = document.createElement('img') as HTMLImageElement;
			img.src = contents;
			viewer.innerHTML = '';
			viewer.appendChild(img);
		};
		reader.readAsDataURL(img);
	};
	const handleLogin = async (form: SubmitEvent) => {
		if(loading) return 0
		const user = form.target['username'].value;
		const password = form.target['password'].value;
		if (!user.length)
			showMessage('username', {
				text: 'Please enter username or email address.',
				variant: 'alert'
			});
		if (!password.length)
			showMessage('password', { text: 'Provide your account password!', variant: 'alert' });
		if (!user.length || !password.length) return 0;
		loading = true
		await axios.post('/api/_users/', createForm({username: user, password}), {
			headers: {
				request: 'signIn'
			}
		})
		.then((res:any)=> {
			loading = false
			res =res.data
			if(res.success === 1){
				message = {message: res.message, variant: 'success'}
				Cookies.set('user', res.user, {expires: 365}) 
				userContextUpdate(res.user)
			}
			if(res.success === 0){
				message = {message: res.message, variant: 'alert'}
			}
		}).catch(err => {
			loading = false
			console.error(err)
			message = {message: err.message, variant: 'danger'}
		})
	};
	let view = 0;
</script>

<div class="form">
	<div class="top-b">
		<button on:click={() => (view = 0)} class={view ? '' : 'active'}>
			<Icon icon="grommet-icons:user-admin" /> Login
		</button>
		<button on:click={() => (view = 1)} class={view ? 'active' : ''}>
			<Icon icon="solar:user-plus-broken" />
			Register
		</button>
	</div>
	{#if view}
		<div transition:slide>
			<h3>BECOME A {WEBSITE_NAME} MEMBER</h3>
			<h5>
				Create your {WEBSITE_NAME} Member profile and get full access to our services and create your
				own gallery, Inspiration and community
			</h5>
			<form on:submit|preventDefault={handelForm}>
				<div class="flex">
					<div class="flx-col">
						<button
							id="image-view"
							class="profile"
							on:click={() => document.getElementById('avatar').click()}
						>
							<Icon icon="teenyicons:user-outline" />
							<span>Browse</span>
						</button>
						<input on:change={handleProfile} type="file" id="avatar" />
					</div>

					<div class="flx-col">
						<label for="username">Enter Username</label>
						<input
							type="text"
							on:keyup={checkUsername}
							id="username"
							placeholder="E.g. littlezabi_"
						/>
					</div>
				</div>
				<div class="flex">
					<div class="flx-col">
						<label for="fullname">Your full name</label>
						<input type="text" id="fullname" placeholder="E.g. John Doe" />
					</div>

					<div class="flx-col">
						<label for="email">Enter email address</label>
						<input type="text" id="email" placeholder="E.g. example123@abc.com" />
					</div>
				</div>
				<div class="flex">
					<div class="flx-col fw">
						<label for="passion">Your Passion (optional)</label>
						<input type="text" id="passion" placeholder="E.g. JavaScript Programmer" />
					</div>
				</div>
				<div class="flex">
					<div class="flx-col">
						<label for="password">Enter your password</label>
						<input type="text" id="password" placeholder="choose a strong password" />
					</div>
					<div class="flx-col">
						<label for="re-pass">Re-enter your password</label>
						<input type="text" id="re-pass" placeholder="Type password again" />
					</div>
				</div>
				<div class="flex">
					<button type="submit" class="submit">
						Sign Up
						{#if loading}
							<span class="message spinner"></span>
						{/if}
					</button>

				</div>
				{#if message}
					<div class="message {message.variant}">{message.message}</div>
				{/if}
			</form>
		</div>
	{:else}
		<div transition:slide>
			<h3>Login Now</h3>
			<h5>
				Login to {WEBSITE_NAME} and get full access to our services and create your own gallery, Inspiration
				and community.
			</h5>
			<form on:submit|preventDefault={handleLogin}>
				<div class="flex">
					<div class="flx-col">
						<label for="username">Enter Username or Email</label>
						<input
							type="text"
							id="username"
							placeholder="E.g. littlezabi_"
						/>
					</div>
				</div>
				<div class="flex">
					<div class="flx-col">
						<label for="password">Enter your password</label>
						<input type="password" id="password" placeholder="choose a strong password" />
					</div>
				</div>
				<div class="flex">
					<button type="submit" class="submit">
						Sign In
						{#if loading}
							<span class="message spinner"></span>
						{/if}
					</button>
				</div>
				{#if message}
					<div class="message {message.variant}">{message.message}</div>
				{/if}
			</form>
		</div>
	{/if}
</div>

<style lang="scss">
	.top-b {
		display: flex;
		align-items: center;
		justify-content: center;
		& button {
			width: 300px;
			background: none;
			color: rgba(255, 255, 255, 0.79);
			border: 1px solid rgba(255, 255, 255, 0.265);
			padding: 5px 0;
			margin-bottom: 5px;
			margin: 0 5px 10px 20px;
			display: flex;
			align-items: center;
			justify-content: center;
			cursor: pointer;
			transition:
				background 200ms linear,
				color 500ms ease-in-out;
			border-radius: 28px;
			&:hover,
			&.active {
				background: rgba(255, 255, 255, 0.627);
				color: black;
			}
		}
	}
	:global(.top-b svg) {
		font-size: 18px;
		margin-right: 10px;
	}
	#avatar {
		display: none;
	}
	:global(.form .profile svg) {
		width: 20px;
		height: 20px;
	}
	:global(.form .profile img) {
		width: 100%;
		height: 100%;
		object-fit: cover;
		border-radius: 50%;
	}
	.profile {
		width: 60px;
		height: 60px;
		display: flex;
		border: 2px solid #ffcfea40;
		border-radius: 50%;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: none;
		font-size: 9px;
		color: rgb(225, 225, 225);
		cursor: pointer;
		padding: 0;
		margin: 0;
		overflow: hidden;
		& span {
			margin-top: 3px;
		}
	}
	:global(.spinner) {
		position: relative;
		&:after {
			position: absolute;
			content: '';
			width: 15px;
			height: 15px;
			border-radius: 50%;
			border: 2px solid rgba(250, 250, 250, 0.176);
			border-left-color: rgb(255, 0, 153);
			margin-left: 10px;
			animation: rotateSpinner 600ms linear forwards infinite;
			@keyframes rotateSpinner {
				100% {
					transform: rotate(360deg);
				}
			}
		}
	}
	.submit {
		width: 250px;
		height: 40px;
		margin: auto;
		cursor: pointer;
		border-radius: 1px;
		background: none;
		margin-top: 10px;
		color: white;
		border: 2px solid rgba(255, 255, 255, 0.595);
		transition: 300ms;
		&:hover {
			background: white;
			color: black;
		}
	}
	input,
	button {
		outline: none;
		font-family: inherit;
	}
	.flx-col {
		display: flex;
		flex-direction: column;
		position: relative;
		& label {
			margin-bottom: 8px;
			margin-top: 8px;
			color: rgb(221, 221, 221);
		}
		width: 100%;
		& input {
			width: 90%;
			height: 24px;
			padding-left: 8px;
			border: none;
			border-bottom: 1px solid #ffffff21;
			background: none;
			position: relative;
			color: white;
			font-size: 14px;
			transition: 300ms;
			&::placeholder {
				color: rgb(191, 191, 191);
			}
			&:hover,
			&:focus {
				border-bottom-color: rgb(255, 0, 89);
			}
		}
		&.fw {
			& input {
				width: 97%;
			}
		}
	}
	.flex {
		margin-top: 15px;
		display: flex;
		align-items: center;
		justify-content: center;
		& .flx-col:nth-child(2) {
			margin-left: 10px;
			& input {
				width: 95%;
			}
		}
	}
	h3 {
		text-transform: uppercase;
		font-size: 20px;
		font-weight: 600;
	}
	h5 {
		margin-top: 6px;
		font-size: 14px;
	}
	.form {
		font-family: var(--secondary-fonts);
		margin: auto;
		max-width: 700px;
		padding: 0px 10px;
	}
</style>
