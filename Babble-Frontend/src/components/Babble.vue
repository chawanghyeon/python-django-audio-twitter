<template>
	<!-- babbles -->
	<div
		class="flex px-3 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
	>
		<router-link :to="`/profile/${babble.user.id}`">
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
		</router-link>
		<div class="ml-3 flex-1 flex flex-col space-y-1">
			<div v-if="babble.rebabbleUser">
				Rebabbleed by {{ babble.rebabbleUser.username }}
			</div>
			<div class="text-sm flex justify-between items-center">
				<router-link :to="`/babble/${babble.id}`">
					<div class="space-x-1">
						<span class="font-bold">{{ babble.user.username }}</span>
						<span class="text-gray-500 text-xs"
							>@{{ babble.user.nickname }}</span
						>
						<span>·</span>
						<span class="text-gray-500 text-xs">{{
							moment(babble.regDate).fromNow()
						}}</span>
					</div>
				</router-link>
				<button
					v-if="currentUser.id === babble.user.id"
					@click="onDeleteBabble(babble.id)"
				>
					<i
						class="fas fa-trash text-red-400 p-2 rounded-full hover:bg-red-50"
					></i>
				</button>
			</div>
			<!-- tag -->
			<div>
				<span v-for="tag in babble.tags" :key="tag">
					<router-link :to="`/${tag}`">
						#{{ tag }}&nbsp;&nbsp;</router-link
					></span
				>
			</div>
			<!-- babble body -->
			<audio-player :audioUrl="babble.fileUrl"></audio-player>
			<!-- babble actions -->
			<div class="flex justify-between">
				<!-- comment button -->
				<div
					@click="showCommentModal = true"
					class="text-gray-500 hover:text-primary"
				>
					<i class="far fa-comment hover:bg-blue-50 rounded-full p-2"></i>
					<span class="ml-1 text-sm">{{ babble.comments.length }}</span>
				</div>
				<!-- rebabble button -->
				<div
					v-if="!isRebabbled"
					class="text-gray-500 hover:text-green-400"
					@click="onInsertRebabble(babble)"
				>
					<i class="fas fa-retweet hover:bg-green-50 rounded-full p-2"></i>
					<span class="ml-1 text-sm">{{ babble.rebabbles.length }}</span>
				</div>
				<div v-else class="text-green-400" @click="onDeleteRebabble()">
					<i class="fas fa-retweet hover:bg-green-50 rounded-full p-2"></i>
					<span class="ml-1 text-sm">{{ babble.rebabbles.length }}</span>
				</div>
				<!-- like button -->
				<div
					v-if="!isLiked"
					class="text-gray-400 hover:text-red-400"
					@click="handleLike(babble)"
				>
					<i class="far fa-heart hover:bg-red-50 rounded-full p-2"></i>
					<span class="ml-1 text-sm">{{ babble.likes.length }}</span>
				</div>
				<div v-else class="text-red-400" @click="handleUnlike(babble.id)">
					<i class="far fa-heart hover:bg-red-50 rounded-full p-2"></i>
					<span class="ml-1 text-sm">{{ babble.likes.length }}</span>
				</div>
				<!-- share button -->
				<div class="text-gray-500 hover:text-primary"></div>
			</div>
		</div>
		<comment-modal
			:babble="babble"
			v-if="showCommentModal"
			@close-modal="onCloseModal"
		></comment-modal>
	</div>
</template>

<script>
import CommentModal from './CommentModal.vue';
import AudioPlayer from './AudioPlayer.vue';
import moment from 'moment';
import { deleteBabble, insertRebabble, like, unlike } from '../api/babble';
import {
	sendRebabbleNotification,
	sendLikeNotification,
} from '../api/babbleElasticsearch.js';
import { ref } from 'vue';

export default {
	components: { CommentModal, AudioPlayer },
	props: ['currentUser', 'babble'],
	methods: {
		onDeleteBabble(babbleId) {
			if (confirm('정말로 배블을 삭제하시겠습니까?')) {
				deleteBabble(babbleId);
				this.isRebabbled = false;
				this.$emit('delete', this.babble);
			}
		},
		async onInsertRebabble(babble) {
			const data = {
				fileUrl: babble.fileUrl,
				tags: babble.tags,
				rebabbleId: babble.id,
			};

			let rebabble = await insertRebabble(data);
			rebabble.data.user.avatar = `http://localhost:88/image/${rebabble.data.user.avatar}`;

			this.$emit('rebabble', rebabble.data);
			this.babble.rebabbles.push(rebabble.data);
			this.isRebabbled = true;

			sendRebabbleNotification(this.babble, this.currentUser);
		},
		onDeleteRebabble() {
			this.babble.rebabbles.forEach(rebabble => {
				if (rebabble.user.id === this.currentUser.id) {
					deleteBabble(rebabble.id);

					let index = this.babble.rebabbles.indexOf(rebabble);
					this.babble.rebabbles.splice(index, 1);

					this.$emit('unrebabble', rebabble.id);
				}
			});

			this.isRebabbled = false;
		},
		handleLike(babble) {
			like(babble.id);
			this.babble.likes.push(this.currentUser);
			this.isLiked = true;
			this.$emit('like', babble);

			sendLikeNotification(this.babble, this.currentUser);
		},
		handleUnlike(babbleId) {
			unlike(babbleId);
			this.babble.likes = this.babble.likes.filter(
				user => user.id != this.currentUser.id
			);
			this.isLiked = false;
			this.$emit('unlike', babbleId);
		},
		onCloseModal(comment) {
			this.babble.comments.push(comment);
			this.showCommentModal = false;
		},
	},
	setup(props) {
		const showCommentModal = ref(false);
		const isRebabbled = ref(false);
		const isLiked = ref(false);

		props.babble.rebabbles.forEach(babble => {
			if (babble.user.id === props.currentUser.id) {
				isRebabbled.value = true;
			}
		});

		props.babble.likes.forEach(l => {
			if (l.id === props.currentUser.id) {
				isLiked.value = true;
			}
		});

		return {
			showCommentModal,
			isRebabbled,
			isLiked,
			moment,
		};
	},
};
</script>

<style></style>
