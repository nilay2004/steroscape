<script lang="ts">
	import Icon from '@iconify/svelte';
	import axios from 'axios';
	import { slide } from 'svelte/transition';
	import { BACKEND_, MAX_RETRY_ATTEMPTS, RETRY_DELAY, REQUEST_TIMEOUT, DEBUG_MODE } from '../lib/config';
	import { onMount, onDestroy } from 'svelte';
	import { userContext, imagesContext, updateImages, SettingsContext } from '../lib/store';
	import Process from './pnrs-graph.svelte';
	// @ts-ignore
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	
	let message = undefined;
	let processStarted = false;
	let ready = false;
	let estimate_time = 0;
	let nerfRes = { iteration: 0, image: false };
	let seriesData: [number?, number?][] = [];
	let process: { [key: string]: { title: string; progress: number } } = {};
	let est_intr = undefined;
	let new_est_time = 0;
	let backendAvailable = false;
	let inProgress = false;
	
	// Helper function to format remaining time
	const showRemainingTime = (time: number) => {
		const hr = Math.floor(time / 3600);
		const min = Math.floor((time % 3600) / 60);
		const sec = (time % 60).toFixed(0);
		let f = '';
		if (hr) f += `${hr} hrs `;
		if (min) f += `${min} min `;
		if (sec) f += `${sec} sec`;
		return f;
	};
	
	// Setup the timer for estimating time
	const estimate_time_interval = () => {
		new_est_time = estimate_time;
		if (!new_est_time) return 0;
		if (est_intr) {
			clearInterval(est_intr);
		}
		est_intr = setInterval(() => {
			if (new_est_time <= 0) {
				new_est_time = 0;
				clearInterval(est_intr);
			} else {
				new_est_time = Math.abs(new_est_time - 1);
			}
		}, 1000);
	};
	
	$: estimate_time, estimate_time_interval();
	
	// Add this helper function after the existing helper functions
	const safeAPICall = async (method, url, options = {}) => {
		if (DEBUG_MODE) console.log(`API ${method} call to ${url}`, options);
		
		try {
			// Set a reasonable timeout
			const timeout = options.timeout || REQUEST_TIMEOUT;
			
			// Add debug headers in debug mode
			const headers = {
				...(options.headers || {}),
				'Accept': 'application/json',
				'X-Client-Version': '1.0.0'
			};
			
			// Add cache-busting parameter for GET requests
			let finalUrl = url;
			if (method.toLowerCase() === 'get') {
				const separator = url.includes('?') ? '&' : '?';
				finalUrl = `${url}${separator}t=${new Date().getTime()}`;
			}
			
			// Make the request
			const response = await axios({
				method,
				url: finalUrl,
				...options,
				headers,
				timeout
			});
			
			if (DEBUG_MODE) console.log(`API response from ${url}:`, response.data);
			return response;
		} catch (error) {
			// Handle network errors
			if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
				console.error(`Timeout error for ${url}:`, error);
				throw new Error(`Request to ${url} timed out. Please try again.`);
			}
			
			if (error.code === 'ERR_NETWORK' || !navigator.onLine) {
				console.error(`Network error for ${url}:`, error);
				throw new Error(`Network error. Please check your internet connection.`);
			}
			
			// Handle server errors with detailed logging
			if (error.response) {
				console.error(`Server error ${error.response.status} for ${url}:`, error.response.data);
				
				// For 500 errors, provide a more user-friendly message
				if (error.response.status === 500) {
					throw new Error(`Server error (500). The server encountered an internal error. Please try again later.`);
				}
				
				// Try to extract error message from response
				const errorMessage = error.response.data?.message || 
					error.response.data?.error || 
					`Server error (${error.response.status})`;
				
				throw new Error(errorMessage);
			}
			
			// For other errors, rethrow with original message
			console.error(`Unhandled error for ${url}:`, error);
			throw error;
		}
	};
	
	// Update the checkBackendAvailability function
	async function checkBackendAvailability() {
		try {
			const response = await fetch(`${BACKEND_}/ping`, { 
				method: 'GET',
				mode: 'cors',
				credentials: 'omit',
				headers: { 
					'Cache-Control': 'no-cache'
				},
				signal: AbortSignal.timeout(3000) // Short timeout for ping
			});
			
			if (response.ok) {
				console.log("Backend is available");
				backendAvailable = true;
				message = false;
				return true;
			} else {
				console.warn("Backend ping failed");
				backendAvailable = false;
				message = { message: 'Backend server not responding - some features may be limited', variant: 'alert' };
				return false;
			}
		} catch (error) {
			console.error("Backend check error:", error);
			backendAvailable = false;
			message = { message: `Backend server not available - ${error.message}`, variant: 'alert' };
			return false;
		}
	}
	
	const getType = (file: File) => (file.type != '' ? file.type : file.name.split('.').pop());
	
	const handleFileInput = async (ev: any) => {
		message = false;
		let f = ev.target.files;
		let files = [...$imagesContext];
		if (
			f[0].type.includes('image/') &&
			files.length === 1 &&
			(getType(files[0]) === 'npz' || getType(files[0]) === 'video/mp4')
		) {
			files = [];
		}
		let isNPZ = getType(f[0]);
		if (
			(files.length === 1 && files[0].type === 'video/mp4') ||
			(files.length === 1 && isNPZ === 'npz')
		)
			files = [];
		if (!files.length) {
			let k = [];
			for (let file of f) {
				const ftype = getType(f);
				if (ftype === 'video/mp4' || ftype === 'npz') {
					k = [file];
					break;
				} else {
					k.push(file);
				}
			}
			updateImages(k);
			return 0;
		}
		for (let i = 0; i < f.length; i++) {
			let item = f[i];
			const ftype = getType(item);
			if (ftype === 'video/mp4' || ftype === 'npz') {
				files = [item];
				break;
			}
			let isExist = false;
			files.map((f: any) => {
				if (f.name === item.name) {
					isExist = true;
					return 0;
				}
			});
			if (!isExist) files.push(item);
		}
		updateImages(files);
	};
	
	// Stop the processing by making a request to the backend
	const stopProcess = async () => {
		if (!processStarted) return;
		
		try {
			message = { message: 'Stopping process...', variant: 'alert' };
			await fetch(`${BACKEND_}/stop-process`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});
			
			processStarted = false;
			estimate_time = 0;
			new_est_time = 0;
			if (est_intr) clearInterval(est_intr);
		} catch (error) {
			console.error("Error stopping process:", error);
			message = { message: 'Failed to stop the process', variant: 'danger' };
		}
	};
	
	onMount(async () => {
		// Check if the backend is available
		await checkBackendAvailability();
		
		// Set up a periodic check (every 30 seconds)
		const intervalId = setInterval(checkBackendAvailability, 30000);
		
		return () => {
			clearInterval(intervalId);
		};
	});
	
	// Now update the tryUpload function to use safer fetch API instead of axios for uploads
	let tryUpload = async () => {
		try {
			if ($imagesContext.length < 3 && $imagesContext.length > 0 && $imagesContext[0].type !== 'video/mp4') {
				message = { message: 'Please select at least 3 images', variant: 'alert' };
				throw new Error('Not enough images selected');
			}

			// Reset and initialize process state
			process = {
				connecting: {
					title: 'Connecting to server',
					progress: 10
				}
			};
			
			// Reset PSNR data
			seriesData = [];

			// First check if server is responding with retry logic
			let serverAvailable = false;
			let retryCount = 0;
			
			while (!serverAvailable && retryCount < MAX_RETRY_ATTEMPTS) {
				try {
					// Ping server to ensure it's available
					const pingResponse = await fetch(`${BACKEND_}/ping`, { 
						method: 'GET',
						headers: { 
							'Accept': 'application/json',
							'Cache-Control': 'no-cache'
						},
						signal: AbortSignal.timeout(5000)
					});
					
					if (pingResponse.ok) {
						serverAvailable = true;
						console.log("Successfully connected to backend server");
					}
				} catch (err) {
					retryCount++;
					console.warn(`Server connection attempt ${retryCount} failed: ${err.message}`);
					
					if (retryCount < MAX_RETRY_ATTEMPTS) {
						// Update UI to show retry attempt
						process = {
							connecting: {
								title: `Connecting to server (retry ${retryCount}/${MAX_RETRY_ATTEMPTS})`,
								progress: Math.min(10 + (retryCount * 10), 30)
							}
						};
						
						// Wait before retrying
						await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
					}
				}
			}
			
			if (!serverAvailable) {
				message = { 
					message: 'Cannot connect to server after multiple attempts. Please verify the server is running.', 
					variant: 'danger' 
				};
				throw new Error('Server connection failed after retries');
			}

			// Mark connection as successful
			process = {
				connecting: {
					title: 'Connected to server',
					progress: 100
				},
				uploading_files: {
					title: 'Preparing upload',
					progress: 0
				}
			};

			// Don't require login, use default user ID
			const userId = $userContext?.id || "default_user";
			
			const form = new FormData();
			for (let file of $imagesContext)
				form.append(`f_${String(Math.floor(Math.random() * 99999))}`, file);
			form.append('user', userId);
			let settings = $SettingsContext;
			delete settings.isOpened;
			form.append('config', JSON.stringify(settings));

			// Start timer for estimating remaining time
			let uploadStartTime = Date.now();
			
			// Use fetch API directly instead of axios for better compatibility
			const response = await fetch(`${BACKEND_}/files`, {
				method: 'POST',
				body: form,
				mode: 'cors',
				credentials: 'omit'
			});
			
			if (!response.ok) {
				throw new Error(`Server error: ${response.status}`);
			}
			
			// Parse the response
			const responseData = await response.json();

			// Process PSNR data if available
			if (responseData && responseData.psnrs && responseData.psnrs.length > 0) {
				// Update the PSNR chart data
				seriesData = responseData.psnrs;
				console.log("Received PSNR data:", seriesData);
			}

			// Mark upload as complete
			process = {
				connecting: {
					title: 'Connected to server',
					progress: 100
				},
				uploading_files: {
					title: 'Upload complete',
					progress: 100
				},
				processing: {
					title: 'Processing complete',
					progress: 100
				}
			};

			return responseData;
		} catch (err) {
			console.error('Upload error details:', err);
			
			// Check for specific network errors
			if (err.name === 'TimeoutError' || err.message.includes('timeout')) {
				console.error('Connection timeout:', err);
				process = {
					...process,
					uploading_files: {
						title: 'Upload timed out',
						progress: 0
					}
				};
				message = { 
					message: 'The connection timed out. Your images may be too large or the server is busy.', 
					variant: 'danger' 
				};
			} else if (err.name === 'TypeError' || !navigator.onLine || err.message.includes('Network Error')) {
				console.error('Network error:', err);
				process = {
					...process,
					uploading_files: {
						title: 'Network error',
						progress: 0
					}
				};
				message = { 
					message: 'Network error. Please check your internet connection and try again.', 
					variant: 'danger' 
				};
			} else if (err.message.includes('413')) {
				// Handle payload too large error
				process = {
					...process,
					uploading_files: {
						title: 'Files too large',
						progress: 0
					}
				};
				message = { 
					message: 'Files are too large. Please reduce the size or number of images.', 
					variant: 'danger' 
				};
			} else if (!message) { // Only set if not already set
				// Handle other errors
				process = {
					...process,
					uploading_files: {
						title: 'Error uploading files',
						progress: 0
					}
				};
				message = { message: err.message || 'Upload failed', variant: 'danger' };
			}
			throw err;
		}
	};

	const dropLeave = (event) => {
		event.target.classList.remove('active');
		try {
			let k = document?.getElementById('m3c2x99k');
			k.textContent = 'Drag one or more files to this';
		} catch (e) {}
	};
	function dragOverHandler(ev) {
		ev.preventDefault();
		ev.target.classList.add('active');
		try {
			let k = document?.getElementById('m3c2x99k');
			k.textContent = "Release to Upload File's";
		} catch (e) {}
	}
	function dropHandler(ev: any) {
		dropLeave(ev);
		message = false;
		ev.preventDefault();
		let files = [...$imagesContext];
		if (files.length === 1 && files[0].type === 'video/mp4') files = [];
		console.log(files);
		if (ev.dataTransfer.items) {
			for (let item of [...ev.dataTransfer.items]) {
				const file = item.getAsFile();
				const isVideo = item.type === 'video/mp4';
				if (isVideo) {
					files = [file];
					break;
				}
				if (item.kind === 'file') {
					let isExist = false;
					$imagesContext.map((f: any) => {
						if (f.name === file.name) {
							isExist = true;
							return 0;
						}
					});
					if (!isExist) files.push(file);
				}
			}
		} else {
			for (let file of [...ev.dataTransfer.files]) {
				const isVideo = file.type === 'video/mp4';
				if (isVideo) {
					files = [file];
					break;
				}
				files.push(file);
			}
		}
		updateImages(files);
	}
	let selectedFileIndex = null;
	const removeFile = () => {
		if (selectedFileIndex) {
			$imagesContext.splice(selectedFileIndex, 1);
			const files = [...$imagesContext];
			updateImages(files);
		} else {
			message = { message: 'No file selected!', variant: 'alert' };
		}
	};
	const showFile = () => {
		const file = $imagesContext[selectedFileIndex];
		const reader = new FileReader();
		reader.onload = (event) => {
			const contents = event.target.result;
			const viewer: any = document.getElementById('image-view');
			viewer.src = contents;
		};
		reader.readAsDataURL(file);
	};
	const clearAll = () => {
		updateImages([]);
		process = {};
		message = false;
	};
	const selectFile = (e: any) => {
		if (e.target.value != 'none') {
			selectedFileIndex = parseInt(e.target.value);
			showFile();
		}
	};
	onDestroy(() => {
		// Clear any timers
		if (est_intr) {
			clearInterval(est_intr);
		}
	});

	const startProcess = async () => {
		if (inProgress) return; // Prevent multiple simultaneous requests
		
		inProgress = true;
		processStarted = true;
		
		// Reset message state and data
		message = null;
		seriesData = [];
		
		try {
			// Check if the backend is available with retry
			const serverAvailable = await checkBackendAvailability();
			
			if (!serverAvailable) {
				message = { 
					message: 'Cannot connect to backend server. Please verify it is running.', 
					variant: 'danger' 
				};
				inProgress = false;
				processStarted = false;
				return;
			}
			
			// Start the upload process
			const uploadResponse = await tryUpload();
			
			if (uploadResponse && uploadResponse.success) {
				// Update process state to show model initialization
				process = {
					connecting: {
						title: 'Connected to server',
						progress: 100
					},
					uploading_files: {
						title: 'Upload complete',
						progress: 100
					},
					processing: {
						title: 'Processing images',
						progress: 20
					}
				};
				
				// Poll the server for status updates
				let processingComplete = false;
				let pollCount = 0;
				let failedPollCount = 0;
				const maxPolls = 600; // Increase poll attempts (20 minutes at 2-second intervals)
				const maxFailedPolls = 5; // Maximum consecutive failed polls before warning
				
				while (!processingComplete && pollCount < maxPolls && failedPollCount < maxFailedPolls) {
					try {
						const statusResponse = await fetch(`${BACKEND_}/processing-status`, { 
							method: 'GET',
							mode: 'cors',
							credentials: 'omit',
							headers: { 
								'Cache-Control': 'no-cache'
							}
						});
						
						if (!statusResponse.ok) {
							throw new Error(`Server returned ${statusResponse.status}`);
						}
						
						const data = await statusResponse.json();
						
						// Reset failed poll counter on success
						failedPollCount = 0;
						
						if (data) {
							const status = data.status;
							const percentage = data.percentage || 0;
							const statusMessage = data.message || 'Processing...';
							
							// Update process information
							process = {
								connecting: {
									title: 'Connected to server',
									progress: 100
								},
								uploading_files: {
									title: 'Upload complete',
									progress: 100
								},
								processing: {
									title: `${statusMessage} (${Math.min(percentage, 99)}%)`,
									progress: Math.min(percentage, 99)
								}
							};
							
							// Check for PSNR data
							if (data && data.psnr) {
								// Extract the PSNR value
								const psnrValue = parseFloat(data.psnr);
								
								// Get current iteration number
								// Use iteration count if we have one, otherwise use pollCount
								const iteration = pollCount; 
								
								// Only add to chart if we have a valid PSNR value
								if (!isNaN(psnrValue)) {
									console.log(`Received PSNR update: ${psnrValue} dB at iteration ${iteration}`);
									
									// Check if we already have this iteration
									const existingIndex = seriesData.findIndex(item => item[0] === iteration);
									if (existingIndex >= 0) {
										// Update existing entry
										seriesData[existingIndex][1] = psnrValue;
									} else {
										// Add new entry
										seriesData = [...seriesData, [iteration, psnrValue]];
									}
									
									// Sort by iteration
									seriesData.sort((a, b) => a[0] - b[0]);
								}
							}
							
							if (status === 'complete') {
								processingComplete = true;
								process = {
									connecting: {
										title: 'Connected to server',
										progress: 100
									},
									uploading_files: {
										title: 'Upload complete',
										progress: 100
									},
									processing: {
										title: 'Processing complete',
										progress: 100
									}
								};
								
								message = { message: 'Processing complete! Your NeRF model is ready.', variant: 'success' };
							} else if (status === 'failed') {
								processingComplete = true;
								message = { 
									message: data.message || 'Processing failed. Please try again.', 
									variant: 'danger' 
								};
								break;
							}
						}
					} catch (err) {
						console.warn(`Failed to get processing status (attempt ${failedPollCount + 1}):`, err);
						failedPollCount++;
						
						// Show warning after consecutive failed polls
						if (failedPollCount >= 3) {
							process = {
								...process,
								processing: {
									...process.processing,
									title: `Processing images (connection issues, retrying...)`
								}
							};
						}
					}
					
					pollCount++;
					await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2 seconds
				}
				
				if (failedPollCount >= maxFailedPolls) {
					message = { 
						message: 'Lost connection to the server. The process may still be running.', 
						variant: 'warning' 
					};
				} else if (!processingComplete && pollCount >= maxPolls) {
					message = { 
						message: 'Processing is taking longer than expected. Please check back later.', 
						variant: 'warning' 
					};
				}
			} else {
				// Upload failed with a server response
				message = { 
					message: uploadResponse?.message || 'Upload failed. Please try again.', 
					variant: 'danger' 
				};
			}
		} catch (error) {
			console.error('Process error:', error);
			// This is handled inside tryUpload() but we'll add a fallback
			if (!message) {
				message = { 
					message: error.message || 'An unexpected error occurred', 
					variant: 'danger' 
				};
			}
		} finally {
			processStarted = false;
			inProgress = false;
		}
	};
</script>

{#if ready}
	<h3>Images is ready</h3>
	<p class="x23">
		Click on start process button to start. before starting make sure you select same object images.
		{#if $imagesContext.length > 40}
			<span style="color: #ff9900;">You have {$imagesContext.length} images. Consider using fewer images (20-30) for better upload performance.</span>
		{/if}
	</p>
{:else}
	<h3>Upload your images or video ✅</h3>
	<p class="x23">
		Enter your images/video of object. only one video is supported of object. add images/video from
		different view points of object. ✔
	</p>
{/if}

{#if ready}
	<div class="_flex ready_" style="justify-content: space-between">
		<div class="xz">
			<h4>{$imagesContext.length > 1 ? $imagesContext.length + ' images' : 'Video'} is ready</h4>
			{#if !processStarted}
				<button class="snd" on:click={() => (ready = false)}>Browse images</button>
			{/if}
			{#each Object.keys(process) as proc}
				<div class="prog-wrap">
					<h5>{process[proc].title} {process[proc].progress}%</h5>
					<div class="prog-out">
						<div class="progress" style={`width: ${process[proc].progress}%`}></div>
					</div>
				</div>
			{/each}
		</div>
		<div class="xy">
			<div class="_flex yt">
				<div class="chart">
					<Process {seriesData} />
				</div>
				{#if nerfRes.image}
					<div class="output" transition:slide={{ axis: 'x' }}>
						<p>Result {nerfRes.iteration} / {$SettingsContext.n_iterations} Iterations</p>
						<img src={BACKEND_ + nerfRes.image} id="result" alt="" />
					</div>
				{/if}
			</div>
			<button
				class="snd snd1 {processStarted ? 'active' : ''}"
				style="margin-top:10px;"
				on:click={startProcess}
			>
				<Icon icon="material-symbols-light:not-started-outline" style="color: #00ccff" />
				START
			</button>
			<button
				class="snd snd2 {!processStarted ? 'active' : ''}"
				style="margin-top:10px;"
				on:click={stopProcess}
			>
				<Icon icon="ic:round-stop" style="color: #ff0040" />
				STOP
			</button>

			{#if estimate_time}
				<span class="time-rem">
					{new_est_time ? `${showRemainingTime(new_est_time)} remaining` : ''}
				</span>
			{/if}
		</div>
	</div>
{:else}
	<div class="_flex">
		<div>
			<input
				type="file"
				id="fileInput"
				multiple
				accept="video/mp4, image/*, .npz"
				on:change={handleFileInput}
				style="display:none;"
			/>
			<div
				class="place"
				role="region"
				aria-labelledby="dropzone-label"
				on:drop={dropHandler}
				on:dragleave={dropLeave}
				on:dragover={dragOverHandler}
			>
				<div>
					<img src="/media/upload.png" alt="upload" />
					<h4 id="m3c2x99k">Drag and drop your images/video.</h4>
					<button on:click={() => document.getElementById('fileInput').click()}>Browse</button>
				</div>
			</div>
		</div>
		{#if $imagesContext.length}
			<div class="right" transition:slide={{ axis: 'x' }}>
				<div class="c2z">
					<h4>Files list</h4>
					<button class="x32" on:click={() => clearAll()}>
						<span>Clear All</span>
						<Icon icon="solar:trash-bin-trash-broken" />
					</button>
				</div>
				<div class="ovx">
					<select class="select" on:change={selectFile}>
						<option value="none">Select image to show</option>
						{#each $imagesContext as file, i}
							<option value={i}>
								{i + 1} - {file.name}
							</option>
						{/each}
					</select>
					<button class="x321" on:click={removeFile}>
						<Icon icon="solar:trash-bin-trash-broken" />
					</button>
				</div>
				<div class="image-viewer" style="display: {selectedFileIndex != null ? 'block' : 'none'}">
					<img src="" id="image-view" alt="" />
				</div>
				<button class="snd" on:click={() => (ready = !ready)}>Ready</button>
			</div>
		{/if}
	</div>
{/if}
{#if message}
	<div class="message {message.variant}">{message.message}</div>
{/if}

<style lang="scss">
	.vid-x {
		width: 221px;
		height: 175px;
		margin: 24px 0px 5px 9px;
		border-radius: 6px;
		object-fit: cover;
	}
	.time-rem {
		font-size: 14px;
		margin-left: 10px;
		width: 255px;
		display: inline-block;
	}
	.output {
		margin-left: 10px;
		& p {
			margin-bottom: 5px;
		}
		& img {
			width: 175px;
			height: 175px;
			border-radius: 4px;
		}
	}
	.ready_ {
		margin-top: 28px;
		& .xz {
			margin-right: 20px;
			& h4 {
				margin-bottom: 10px;
			}
			& button {
				border: none;
				padding: 0;
				width: max-content;
				height: max-content;
				color: dodgerblue;
				font-weight: bold;
				text-decoration: underline;
				&:hover {
					background: none;
					color: white !important;
				}
			}
		}
		& .xy {
			margin-left: 20px;
		}
	}
	.image-viewer {
		margin-bottom: 13px;
		& img {
			width: 100%;
			height: 151px;
			object-fit: contain;
		}
	}
	.select {
		width: 250px;
		margin: 10px 10px 0 10px;
		height: 40px;
		border-radius: 28px;
		background: #090918;
		outline: none;
		border: 2px solid white;
		padding: 0 8px;
		cursor: pointer;
		color: white;
		& option {
			color: white;
			background: #090918;
		}
	}
	.prog-wrap {
		margin: 20px auto 5px auto;
		& h5 {
			margin-bottom: 5px;
		}
	}
	.prog-out {
		display: flex;
		height: 3px;
		width: 300px;
		background: #0000004f;
		border-radius: 18px;
		border: 1px solid #ffffff0f;
	}
	.progress {
		height: 100%;
		background: linear-gradient(45deg, #ff0052, #fb0079, #ff008b, #ff2b00);
		border-radius: 18px;
		transition: 300ms linear;
	}
	.snd {
		width: 100px;
		height: 40px;
		margin: auto;
		margin-right: 10px;
		margin-bottom: 10px;
		background: none;
		color: white;
		border: 2px solid #ffffff4a;
		border-radius: 3px;
		text-transform: uppercase;
		font-family: inherit;
		cursor: pointer;
		transition: 300ms;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		&.snd1 {
			background: #00ff9126;
			border-color: #00ff9126;
			&:hover {
				background: #00ff9136;
			}
		}
		&.snd2 {
			background: #ff006a4e;
			border-color: #ff006a4e;
			&:hover {
				background: #ff008c67;
			}
		}
		&.active {
			opacity: 0.3;
			&.snd1 {
				&:hover {
					background: #00ff9126;
				}
			}
			&.snd2 {
				&:hover {
					background: #ff006a4e;
				}
			}
		}
		// &:hover {
		// 	background: white;
		// 	color: black;
		// }
	}
	:global(.snd svg) {
		font-size: 28px;
		margin-right: 8px;
	}
	:global(.c2z button svg) {
		font-size: 16px;
	}
	.c2z {
		display: flex;
		justify-content: space-between;
		align-items: center;
		& h4 {
			font-size: 18px;
		}
		& button {
			display: flex;
			align-items: center;
			border: none;
			border-bottom: 2px solid #ff002f;
			background: none;
			color: white;
			font-family: inherit;
			padding-bottom: 4px;
			cursor: pointer;
			transition: 300ms;
			&:hover {
				color: #ff5e7c !important;
			}
			& span {
				margin-right: 8px;
			}
		}
	}
	.right {
		margin-left: 40px;
		max-height: 400px;
		& .ovx {
			margin-top: 10px;
			margin-bottom: 30px;
			width: 100%;
			display: flex;
			align-items: center;
			justify-content: center;
		}
	}
	.x32 {
		font-size: 16px;
	}
	.x321 {
		background: none;
		border: none;
		margin-top: 10px;
		color: #ff0015;
		&:hover {
			color: #e600ff;
		}
		font-size: 22px;
		cursor: pointer;
	}
	h3 {
		font-size: 22px;
		margin: 5px 0px 0px 0px;
	}
	.x23 {
		margin-bottom: 10px;
		font-size: 14px;
		margin-top: 5px;
	}

	._flex {
		display: flex;
	}
	.place {
		width: 400px;
		height: 300px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 2px dashed grey;
		border-radius: 18px;
		text-align: center;
		&.active {
			border-color: #00e6ff;
		}
		& h4 {
			margin-bottom: 10px;
			color: grey;
		}
		& button {
			width: 250px;
			height: 40px;
			background: none;
			border: 2px solid rgb(133, 133, 133);
			color: white;
			border-radius: 25px;
			cursor: pointer;
			transition: all 300ms ease-in;
			font-family: inherit;
			&:hover {
				background: white;
				color: black;
			}
		}
		& img {
			width: 40px;
			filter: invert(1);
		}
	}
</style>
