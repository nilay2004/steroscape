<script lang="ts">
	import { life } from '../lib/globals';
	const dayPortion = life(Date()).dayPortion();
</script>

<h1 class="main-day-portion">
	{dayPortion[0]}
	<span>
		Today is {life(Date()).format('D Mm, YYYY')}
		{dayPortion[1]}.
	</span>
</h1>
