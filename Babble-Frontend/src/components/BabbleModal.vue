<template>
	<div class="fixed z-10 inset-0 overflow-y-auto" @click="$emit('close-modal')">
		<div
			class="flex justify-center min-h-screen sm:pt-6 sm:px-4 sm:pb-20 text-center sm:block sm:p-0"
		>
			<div class="fixed inset-0 transition-opacity" aria-hidden="true">
				<div class="absolute inset-0 bg-gray-500 opacity-75"></div>
			</div>
			<!-- contents -->
			<div
				@click.stop
				class="inline-block bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg w-full"
				role="dialog"
				aria-modal="true"
				aria-labelledby="modal-headline"
			>
				<div
					class="border-b border-gray-100 p-2 flex items-center justify-between"
				>
					<button
						@click="$emit('close-modal')"
						class="fas fa-times text-primary text-lg p-2 h-10 w-10 hover:bg-blue-50 rounded-full"
					></button>
				</div>
				<!-- babble section -->
				<div class="flex p-4">
					<img
						v-if="currentUser.avatar.slice(-4) !== 'null'"
						:src="currentUser.avatar"
						class="w-10 h-10 rounded-full hover:opacity-80 cursor-pointer"
					/>
					<img
						v-else
						src="../image/defaultProfile.png"
						class="w-10 h-10 rounded-full hover:opacity-80 cursor-pointer"
					/>
					<div class="ml-2 flex-1 flex flex-col">
						<audio-recorder @close-modal="closeModal" />
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import AudioRecorder from './audioRecorder/recorder.vue';
import store from '../store';
import { computed } from 'vue';

export default {
	components: { AudioRecorder },
	setup(props, { emit }) {
		const currentUser = computed(() => store.state.user);

		const closeModal = () => {
			emit('close-modal');
		};

		return {
			currentUser,
			closeModal,
		};
	},
};
</script>

<style></style>
