<template>
	<div @click="play()">Listen Babble</div>
</template>
<script>
import server from '../api/constants';
export default {
	props: ['id'],
	data: function () {
		return {
			isPlaying: false,
			isLoaded: false,
			audio: '',
		};
	},
	watch: {
		$route() {
			if (this.audio) {
				this.audio.pause();
				this.audio = null;
			}
		},
	},
	methods: {
		play() {
			if (!this.isLoaded) {
				this.audio = new Audio(`${server}/babble/${this.id}`);
				this.isLoaded = true;
			}
			if (!this.isPlaying) {
				this.audio.play();
				this.isPlaying = true;
			} else {
				this.audio.pause();
				this.isPlaying = false;
			}
		},
	},
};
</script>
