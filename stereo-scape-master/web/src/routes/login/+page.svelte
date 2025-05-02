<script>
	import { onMount } from 'svelte';
	import axios from 'axios';
	import { userContext } from '../../lib/store';

	let username = '';
	let password = '';
	let message = '';

	const handleLogin = async () => {
		if (!username || !password) {
			message = 'Please fill in all fields';
			return;
		}

		try {
			const response = await fetch('/api/_users?login=true', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			const data = await response.json();

			if (data.success) {
				// Set user context
				$userContext = data.user;
				// Redirect to home
				window.location.href = '/';
			} else {
				message = data.message || 'Login failed';
			}
		} catch (error) {
			console.error('Login error:', error);
			message = 'An error occurred during login';
		}
	};

	onMount(() => {
		// Check if user is already logged in
		if ($userContext && $userContext.id) {
			window.location.href = '/';
		}
	});
</script>

<svelte:head>
	<title>Login - StereoScape</title>
</svelte:head>

<div class="login-container">
	<div class="login-form">
		<h2>Login to Your Account</h2>
		
		{#if message}
			<div class="message error">{message}</div>
		{/if}

		<div class="form-group">
			<label for="username">Username</label>
			<input type="text" id="username" bind:value={username} placeholder="Enter your username" />
		</div>

		<div class="form-group">
			<label for="password">Password</label>
			<input type="password" id="password" bind:value={password} placeholder="Enter your password" />
		</div>

		<button on:click={handleLogin} class="login-button">Login</button>

		<div class="signup-link">
			Don't have an account? <a href="/sign-up">Sign up here</a>
		</div>
	</div>
</div>

<style>
	.login-container {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 80vh;
		padding: 20px;
	}

	.login-form {
		background: #fff;
		border-radius: 8px;
		box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
		padding: 40px;
		width: 100%;
		max-width: 400px;
	}

	h2 {
		text-align: center;
		margin-bottom: 30px;
		color: #333;
	}

	.form-group {
		margin-bottom: 20px;
	}

	label {
		display: block;
		margin-bottom: 8px;
		font-weight: 500;
		color: #555;
	}

	input {
		width: 100%;
		padding: 12px;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 16px;
		transition: border-color 0.3s;
	}

	input:focus {
		border-color: #4a90e2;
		outline: none;
	}

	.login-button {
		width: 100%;
		padding: 12px;
		background-color: #4a90e2;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 16px;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.login-button:hover {
		background-color: #3a7bc8;
	}

	.signup-link {
		text-align: center;
		margin-top: 20px;
		font-size: 14px;
		color: #666;
	}

	.signup-link a {
		color: #4a90e2;
		text-decoration: none;
	}

	.signup-link a:hover {
		text-decoration: underline;
	}

	.message {
		padding: 10px;
		margin-bottom: 20px;
		border-radius: 4px;
		text-align: center;
	}

	.error {
		background-color: #ffebee;
		color: #c62828;
		border: 1px solid #ffcdd2;
	}
</style> 