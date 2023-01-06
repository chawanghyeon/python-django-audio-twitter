<template>
	<div @click="play()">Listen Babble</div>
</template>
<script>
export default {
	props: ['audioUrl'],
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
		async play() {
			if (!this.isLoaded) {
				this.audio = new Audio(`http://localhost:88/audio/${this.audioUrl}`);
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
