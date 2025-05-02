<script lang="ts">
	import Highcharts from 'highcharts';
	import { onMount } from 'svelte';
	// @ts-ignore
	import { getRandomChar } from '$lib/globals';
	export let seriesData: any = [];
	export let config: {
		width?: number;
		height?: number;
		xAxis?: boolean;
		yAxis?: boolean;
		title?: boolean | string;
		background?: string;
		line_color?: string | { linearGradient: number[]; stops: any[] };
	} = {};
	let setting = {
		line_color: {
			linearGradient: [0, 0, 400, 400],
			stops: [
				[0, '#ff3c60'],
				[0.3, '#00beff'],
				[0.6, '#00ff0e'],
				[0.9, '#fff900']
			]
		},
		width: 320,
		height: 200,
		xAxis: true,
		yAxis: true,
		title: true,
		background: '#172353b0',
		...config
	};
	let Chart = null;
	let element_id = 'id_' + getRandomChar(10);
	let chartInitialized = false;

	// Add basic error handling to prevent chart errors
	const updateChart = (series: any) => {
		try {
			if (!Chart) {
				console.warn("Chart is not initialized yet");
				return;
			}
			
			if (!series || !Array.isArray(series) || series.length === 0) {
				// Clear the chart data if no data is available
				Chart.series[0].setData([], true);
				return;
			}
			
			// Make sure all data points are valid
			const validDataPoints = series.filter(point => 
				Array.isArray(point) && 
				point.length === 2 && 
				!isNaN(point[0]) && 
				!isNaN(point[1])
			);
			
			if (validDataPoints.length === 0) {
				console.warn("No valid data points found in series");
				Chart.series[0].setData([], true);
				return;
			}
			
			// Extract x and y values for chart
			const iterations = validDataPoints.map(d => d[0]);
			const psnrValues = validDataPoints.map(d => d[1]);
			
			// Update chart data
			Chart.xAxis[0].setCategories(iterations);
			Chart.series[0].setData(psnrValues, true, false, true);
			
			// Update ranges and redraw
			if (psnrValues.length > 0) {
				const minPSNR = Math.min(...psnrValues) * 0.95; // Give some margin
				const maxPSNR = Math.max(...psnrValues) * 1.05;
				
				Chart.yAxis[0].setExtremes(minPSNR, maxPSNR);
			}
			
			// Make sure chart is visible
			Chart.redraw();
		} catch (err) {
			console.error("Error updating PSNR chart:", err);
		}
	};

	// Watch for data changes
	$: {
		if (seriesData && chartInitialized) {
			updateChart(seriesData);
		}
	}

	onMount(() => {
		try {
			// Configure Highcharts global options
			Highcharts.setOptions({
				chart: {
					animation: false, // Disable animations for better performance
					style: {
						fontFamily: 'inherit',
						fontSize: '11px'
					}
				}
			});
			
			// Create the chart
			Chart = Highcharts.chart(element_id, {
				credits: {
					enabled: false
				},
				chart: {
					type: 'spline',
					backgroundColor: setting.background,
					height: setting.height,
					width: setting.width,
					style: {
						fontFamily: 'inherit',
						fontSize: '11px',
						borderRadius: '3px'
					},
					events: {
						load: function() {
							chartInitialized = true;
							if (seriesData && seriesData.length > 0) {
								updateChart(seriesData);
							}
						}
					}
				},
				plotBackgroundColor: null,
				title: setting.title
					? {
							text: 'PSNR (Peak Signal-to-Noise Ratio)',
							style: { color: 'white' }
						}
					: null,
				subtitle: null,
				xAxis: setting.xAxis
					? {
							lineWidth: 0,
							gridLineWidth: 0,
							minorGridLineWidth: 0,
							categories: [],
							labels: {
								style: { color: 'white' },
								enabled: true,
								format: '{text}'
							},
							title: {
								text: 'Iteration',
								style: { color: 'white' }
							}
						}
					: {
							text: null,
							gridLineWidth: 0,
							minorGridLineWidth: 0,
							tickWidth: 0,
							lineWidth: 0,
							labels: { enabled: false }
						},
				yAxis: setting.yAxis
					? {
							gridLineWidth: 0.2,
							labels: {
								style: { color: 'white' },
								enabled: true,
								format: '{value} dB'
							},
							title: {
								text: 'PSNR (dB)',
								style: { color: 'white' }
							}
						}
					: { title: { text: null }, gridLineWidth: 0, labels: { enabled: false } },
				tooltip: {
					formatter: function () {
						return (
							`<b>PSNR PER ITERATION</b><br>` +
							'Iteration: ' +
							this.x +
							'<br>' +
							'PSNR: ' +
							this.y.toFixed(4) + ' dB'
						);
					}
				},
				plotOptions: {
					spline: {
						dataLabels: {
							enabled: false
						},
						marker: {
							enabled: true,
							radius: 2,
							states: {
								hover: {
									enabled: true,
									radius: 4
								}
							}
						}
					}
				},
				legend: {
					enabled: false
				},
				series: [
					{
						name: 'PSNR',
						color: setting.line_color,
						data: seriesData.map((d) => d[1])
					}
				]
			});
		} catch (err) {
			console.error("Error initializing PSNR chart:", err);
		}
	});
</script>

<div id={element_id} />
