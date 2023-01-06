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
					<!-- babble button -->
					<div class="text-right sm:hidden mr-2">
						<button
							v-if="!babbleBody.length"
							class="bg-light text-sm font-bold text-white px-4 py-1 rounded-full"
						>
							답글
						</button>
						<button
							v-else
							@click="onCommentBabble"
							class="bg-primary hover:bg-dark text-sm font-bold text-white px-4 py-1 rounded-full"
						>
							답글
						</button>
					</div>
				</div>
				<div>
					<!-- original babble -->
					<div class="flex px-4 pt-4 pb-3">
						<div class="flex flex-col">
							<img
								v-if="babble.user.avatar.slice(-4) !== 'null'"
								:src="babble.user.avatar"
								class="w-10 h-10 rounded-full hover:opacity-80 cursor-pointer"
							/>
							<img
								v-else
								src="../image/defaultProfile.png"
								class="w-10 h-10 rounded-full hover:opacity-80 cursor-pointer"
							/>
							<div class="ml-5 w-0.5 h-full bg-gray-300 mt-2 -mb-1"></div>
						</div>
						<div class="ml-2 flex-1">
							<div class="flex space-x-2">
								<span class="font-bold text-sm">{{
									babble.user.username
								}}</span>
								<span class="text-gray text-sm"
									>@{{ babble.user.nickname }}</span
								>
								<span class="text-gray text-sm">{{
									moment(babble.regDate).fromNow()
								}}</span>
							</div>
							<div>
								<span class="text-primary text-sm"
									>@{{ babble.user.nickname }}</span
								>
								<span class="text-gray text-sm"> 님에게 보내는 답글</span>
							</div>
						</div>
					</div>
					<!-- babbleing section -->
					<div class="flex px-4 pb-4">
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
						<audio-recorder @insert-comment="onCommentBabble" />
						<!-- babble button -->
						<!-- <div class="text-right hidden sm:block">
								<button
									v-if="!babbleBody.length"
									class="bg-light text-sm font-bold text-white px-4 py-1 rounded-full"
								>
									답글
								</button>
								<button
									v-else
									@click="onCommentBabble"
									class="bg-primary hover:bg-dark text-sm font-bold text-white px-4 py-1 rounded-full"
								>
									답글
								</button>
							</div> -->
						<!-- </div> -->
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { ref, computed } from 'vue';
import moment from 'moment';
import store from '../store/index';
import { insertComment } from '../api/babble';
import AudioRecorder from './audioRecorder/recorder.vue';
import { sendCommentNotification } from '../api/babbleElasticsearch.js';

export default {
	props: ['babble'],
	components: { AudioRecorder },
	setup(props, { emit }) {
		const babbleBody = ref('');
		const currentUser = computed(() => store.state.user);

		if (props.babble) {
			store.commit('SET_ISCOMMENTMODAL', true);
		}

		const onCommentBabble = async () => {
			const data = {
				babble: {
					id: props.babble.id,
				},
				fileUrl: store.state.checkedAudio.name,
			};
			let comment = await insertComment(props.babble.id, data);

			store.commit('SET_ISCOMMENTMODAL', false);
			store.commit('SET_CHECKEDAUDIO', null);
			emit('close-modal', comment.data);

			sendCommentNotification(props.babble, currentUser.value);
		};

		return {
			onCommentBabble,
			currentUser,
			babbleBody,
			moment,
		};
	},
};
</script>

<style></style>
