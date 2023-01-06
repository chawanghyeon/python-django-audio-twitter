<template>
	<div class="flex-1 flex">
		<div class="flex-1 border-r border-gray-100">
			<div class="flex flex-col" v-if="babble">
				<!-- title -->
				<div class="flex items-center px-3 py-2 border-b border-gray-100">
					<button @click="router.go(-1)">
						<i
							class="fas fa-arrow-left text-primary text-lg ml-3 hover:bg-blue-50 p-2 rounded-full h-10 w-10"
						></i>
					</button>
					<span class="font-bold text-lg ml-6">트윗</span>
				</div>
				<!-- babble -->
				<div class="px-3 py-2 flex">
					<img
						v-if="babble.user.avatar.slice(-4) !== 'null'"
						:src="babble.user.avatar"
						class="w-10 h-10 rounded-full hover:opacity-90 cursor-pointer"
					/>
					<img
						v-else
						src="../image/defaultProfile.png"
						class="w-10 h-10 rounded-full hover:opacity-90 cursor-pointer"
					/>
					<div class="ml-2">
						<div class="font-bold">{{ babble.user.username }}</div>
						<div class="text-gray text-sm">@{{ babble.user.nickname }}</div>
					</div>
				</div>
				<div class="tag">
					<span v-for="tag in babble.tags" :key="tag">
						<router-link :to="`/${tag}`">
							#{{ tag }}&nbsp;&nbsp;</router-link
						></span
					>
				</div>
				<detail-audio-player
					class="px-3 py-2"
					:audioUrl="babble.fileUrl"
					playerid="audio-player"
				></detail-audio-player>
				<div class="px-3 py-2 text-gray text-xs">
					{{ moment(babble.regDate).fromNow() }}
				</div>
				<div class="h-px w-full bg-gray-100"></div>
				<div class="flex space-x-2 px-3 py-2 items-center">
					<span class="">{{ babble.rebabbles.length }}</span>
					<span class="text-sm text-gray">리배블</span>
					<span class="ml-5">{{ babble.likes.length }}</span>
					<span class="text-sm text-gray">마음에 들어요</span>
				</div>
				<div class="h-px w-full bg-gray-100"></div>
				<!-- buttons -->
				<div class="flex justify-around py-2">
					<button @click="showCommentModal = true">
						<i
							class="far fa-comment text-gray-400 text-xl hover:bg-blue-50 hover:text-primary p-2 rounded-full h-10 w-10"
						></i>
					</button>
					<button @click="onRebabble()">
						<i
							v-if="isRebabbled"
							class="fas fa-retweet text-xl hover:bg-green-50 text-green-400 p-2 rounded-full h-10 w-10"
						></i>
						<i
							v-else
							class="fas fa-retweet text-gray-400 text-xl hover:bg-green-50 hover:text-green-400 p-2 rounded-full h-10 w-10"
						></i>
					</button>
					<button @click="handleLikes()">
						<i
							v-if="this.isLiked"
							class="far fa-heart text-xl hover:bg-red-50 text-red-400 p-2 rounded-full h-10 w-10"
						></i>
						<i
							v-else
							class="far fa-heart text-gray-400 text-xl hover:bg-red-50 hover:text-red-400 p-2 rounded-full h-10 w-10"
						></i>
					</button>
				</div>
				<div class="h-px w-full bg-gray-100"></div>
				<!-- comments -->
				<div
					v-for="comment in babble.comments"
					:key="comment"
					class="flex hover:bg-gray-50 cursor-pointer px-3 py-3 border-b border-gray-100"
				>
					<img
						v-if="comment.user.avatar.slice(-4) !== 'null'"
						:src="comment.user.avatar"
						class="w-10 h-10 rounded-full hover:opacity-90 cursor-pointer"
					/>
					<img
						v-else
						src="../image/defaultProfile.png"
						class="w-10 h-10 rounded-full hover:opacity-90 cursor-pointer"
					/>
					<div class="ml-2 flex-1">
						<div class="flex items-center space-x-2">
							<span class="font-bold">{{ comment.user.username }}</span>
							<span class="text-gray text-sm"
								>@{{ comment.user.nickname }}</span
							>
							<span>{{ moment(comment.regDate).fromNow() }}</span>
						</div>
						<audio-player
							class="px-3 py-2"
							:audioUrl="comment.fileUrl"
						></audio-player>
					</div>
					<button
						@click="onDeleteComment(comment.id)"
						v-if="comment.user.id === currentUser.id"
					>
						<i
							class="fas fa-trash text-red-400 hover:bg-red-50 w-10 h-10 rounded-full p-2"
						></i>
					</button>
				</div>
			</div>
		</div>
		<comment-modal
			:babble="babble"
			v-if="showCommentModal"
			@close-modal="onAddComment"
		></comment-modal>
	</div>
</template>

<script>
import DetailAudioPlayer from '../components/DetailAudioPlayer.vue';
import CommentModal from '../components/CommentModal.vue';
import AudioPlayer from '../components/AudioPlayer.vue';
import router from '../router';
import store from '../store';
import moment from 'moment';
import { onBeforeMount, ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import {
	insertRebabble,
	deleteComment,
	deleteBabble,
	getBabble,
	unlike,
	like,
} from '../api/babble.js';
import {
	sendCommentNotification,
	sendRebabbleNotification,
	sendLikeNotification,
} from '../api/babbleElasticsearch.js';

export default {
	components: { CommentModal, AudioPlayer, DetailAudioPlayer },
	methods: {
		onAddComment(comment) {
			if (comment) {
				comment.user.avatar = `http://localhost:88/image/${comment.user.avatar}`;
				this.babble.comments.push(comment);
			}
			this.showCommentModal = false;

			sendCommentNotification(this.babble, this.currentUser);
		},
		onDeleteComment(commentId) {
			if (confirm('정말로 답글을 삭제하시겠습니까?')) {
				deleteComment(this.babble.id, commentId);
				this.babble.comments = this.babble.comments.filter(
					comment => comment.id !== commentId
				);
			}
		},
		async onRebabble() {
			if (this.isRebabbled) {
				this.babble.rebabbles.forEach(rebabble => {
					if (rebabble.user.id === this.currentUser.id) {
						deleteBabble(rebabble.id);

						let index = this.babble.rebabbles.indexOf(rebabble);
						this.babble.rebabbles.splice(index, 1);
					}
				});
				this.isRebabbled = false;
			} else {
				const data = {
					fileUrl: this.babble.fileUrl,
					tags: this.babble.tags,
					rebabbleId: this.babble.id,
				};

				const rebabble = await insertRebabble(data);
				this.babble.rebabbles.push(rebabble.data);
				this.isRebabbled = true;

				sendRebabbleNotification(this.babble, this.currentUser);
			}
		},
		async handleLikes() {
			if (this.isLiked) {
				unlike(this.babble.id);
				this.babble.likes = this.babble.likes.filter(
					user => user.id !== this.currentUser.id
				);
				this.isLiked = false;
			} else {
				like(this.babble.id);
				this.babble.likes.push(this.currentUser);
				this.isLiked = true;

				sendLikeNotification(this.babble, this.currentUser);
			}
		},
	},
	setup() {
		const currentUser = computed(() => store.state.user);
		const showCommentModal = ref(false);
		const isRebabbled = ref(false);
		const isLiked = ref(false);
		const babble = ref(null);
		const comments = ref([]);
		const route = useRoute();

		onBeforeMount(async () => {
			let data = await getBabble(route.params.id);
			babble.value = data.data;
			babble.value.user.avatar = `http://localhost:88/image/${babble.value.user.avatar}`;

			babble.value.comments.forEach(comment => {
				comment.user.avatar = `http://localhost:88/image/${comment.user.avatar}`;
			});

			babble.value.rebabbles.forEach(babble => {
				if (babble.user.id === currentUser.value.id) {
					isRebabbled.value = true;
				}
			});

			babble.value.likes.forEach(like => {
				if (like.id === currentUser.value.id) {
					isLiked.value = true;
				}
			});
		});
		return {
			showCommentModal,
			currentUser,
			isRebabbled,
			comments,
			isLiked,
			router,
			babble,
			moment,
		};
	},
};
</script>

<style>
.tag {
	margin-left: 20px;
}
</style>
