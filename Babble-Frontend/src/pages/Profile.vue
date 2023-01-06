<template>
	<div class="flex-1 flex" v-if="profileUser">
		<!-- profile section -->
		<div class="flex-1 flex flex-col border-r border-color">
			<!-- title -->
			<div class="px-3 py-1 flex border-b border-color">
				<button class="mr-4" @click="router.go(-1)">
					<i
						class="fas fa-arrow-left text-primary p-3 rounded-full hover:bg-blue-50"
					></i>
				</button>
				<div>
					<div class="font-extrabold text-lg">{{ profileUser.username }}</div>
					<div class="text-xs text-gray">{{ babbles.length }} 배블</div>
				</div>
			</div>
			<!-- background image -->
			<div class="bg-gray-300 h-48 relative flex-none">
				<img
					v-if="$store.state.user.avatar.slice(-4) !== 'null'"
					:src="profileUser.background"
					class="w-full h-48 object-cover"
				/>
				<img
					v-else
					src="../image/defaultBackground.jpg"
					class="w-full h-48 object-cover"
				/>
				<!-- profile image -->
				<div
					class="border-4 border-white bg-gray-100 w-28 h-28 rounded-full absolute -bottom-14 left-2"
				>
					<img
						v-if="profileUser.avatar.slice(-4) !== 'null'"
						:src="profileUser.avatar"
						class="w-full h-full rounded-full opacity-90 hover:opacity-100 cursor-pointer"
					/>
					<img
						v-else
						src="../image/defaultProfile.png"
						class="w-full h-full rounded-full opacity-90 hover:opacity-100 cursor-pointer"
					/>
				</div>
			</div>
			<!-- profile edit button -->
			<div class="text-right mt-2 mr-2 mb-10 relative">
				<div v-if="currentUser.id === profileUser.id">
					<button
						@click="showProfileEditModal = true"
						class="border text-sm border-primary text-primary px-3 py-2 hover:bg-blue-50 font-bold rounded-full"
					>
						프로필 수정
					</button>
				</div>
				<div v-else>
					<div v-if="isFollowed" class="" @click="onUnFollow">
						<button
							class="absolute w-24 right-0 text-sm bg-primary text-white px-3 py-2 hover:opacity-0 font-bold rounded-full"
						>
							팔로잉
						</button>
						<button
							class="absolute w-24 right-0 text-sm bg-red-400 text-white px-3 py-2 opacity-0 hover:opacity-100 font-bold rounded-full"
						>
							언팔로우
						</button>
					</div>
					<div v-else @click="onFollow">
						<button
							class="absolute right-0 w-24 border text-sm border-primary text-primary px-3 py-2 hover:bg-blue-50 font-bold rounded-full"
						>
							팔로우
						</button>
					</div>
				</div>
			</div>
			<!-- user info -->
			<div class="mx-3 mt-2">
				<div class="font-extrabold text-lg">
					{{ profileUser.lastName + profileUser.firstName }}
				</div>
				<div class="text-gray">@{{ profileUser.nickname }}</div>
				<div>{{ profileUser.bio }}</div>
				<div>
					<span class="text-gray">가입일: </span>
					<span class="text-gray">{{
						moment(profileUser.regDate).format('YYYY년 MM월')
					}}</span>
				</div>
				<div>
					<span class="font-bold mr-1">{{
						profileUser.followings.length
					}}</span>
					<span class="text-gray mr-3">팔로우 중</span>
					<span class="font-bold mr-1">{{ profileUser.followers.length }}</span>
					<span class="text-gray">팔로워</span>
				</div>
			</div>
			<!-- tabs -->
			<div class="flex border-b border-color mt-3">
				<div
					@click="currentTab = 'babble'"
					:class="`${
						currentTab == 'babble'
							? 'border-b border-primary text-primary'
							: ' text-gray'
					} py-3  font-bold  text-center w-1/3 hover:bg-blue-50 cursor-pointer hover:text-primary`"
				>
					배블
				</div>
				<div
					@click="currentTab = 'rebabble'"
					:class="`${
						currentTab == 'rebabble'
							? 'border-b border-primary text-primary'
							: ' text-gray'
					} py-3  font-bold  text-center w-1/3 hover:bg-blue-50 cursor-pointer hover:text-primary`"
				>
					리배블
				</div>
				<div
					@click="currentTab = 'like'"
					:class="`${
						currentTab == 'like'
							? 'border-b border-primary text-primary'
							: ' text-gray'
					} py-3  font-bold  text-center w-1/3 hover:bg-blue-50 cursor-pointer hover:text-primary`"
				>
					좋아요
				</div>
			</div>
			<!-- babbles -->
			<div class="overflow-y-auto">
				<Babble
					v-for="babble in currentTab == 'babble'
						? babbles
						: currentTab == 'rebabble'
						? rebabbles
						: profileUser.likeBabbles"
					:key="babble.id"
					:currentUser="currentUser"
					:babble="babble"
					@delete="deleteBabble"
					@unrebabble="deleteRebabble"
					@rebabble="addRebabble"
					@like="addLike"
					@unlike="deleteLike"
				/>
			</div>
		</div>
		<profile-edit-modal
			v-if="showProfileEditModal"
			@close-modal="editProfileUser"
		></profile-edit-modal>
	</div>
</template>

<script>
import ProfileEditModal from '../components/ProfileEditModal.vue';
import AudioPlayer from '../components/AudioPlayer.vue';
import Babble from '../components/Babble.vue';
import router from '../router';
import moment from 'moment';
import store from '../store';
import { sendFollowNotification } from '../api/babbleElasticsearch';
import { computed, ref, onBeforeMount } from 'vue';
import { getUser, follow, unfollow } from '../api/babble';
import { useRoute } from 'vue-router';

export default {
	components: { Babble, ProfileEditModal, AudioPlayer },
	methods: {
		deleteBabble(babble) {
			this.babbles = this.babbles.filter(t => t !== babble);
		},
		deleteRebabble(babbleId) {
			this.rebabbles = this.rebabbles.filter(t => t.id !== babbleId);
		},
		addRebabble(babble) {
			if (this.profileUser.id === this.currentUser.id) {
				this.rebabbles.push(babble);
			}
		},
		editProfileUser() {
			this.showProfileEditModal = false;
			window.location.reload();
		},
		addLike(babble) {
			if (this.profileUser.id === this.currentUser.id) {
				this.profileUser.likeBabbles.push(babble);
			}
		},
		deleteLike(babbleId) {
			this.profileUser.likeBabbles = this.profileUser.likeBabbles.filter(
				t => t.id !== babbleId
			);
		},
	},
	computed: {
		isFollowed() {
			let status = false;
			this.profileUser.followers.forEach(user => {
				if (user.id === this.currentUser.id) {
					status = true;
				}
			});
			return status;
		},
	},
	watch: {
		'$route.params.id'() {
			window.location.reload();
		},
	},
	setup() {
		const currentUser = computed(() => store.state.user);
		const showProfileEditModal = ref(false);
		const currentTab = ref('babble');
		const profileUser = ref(null);
		const rebabbles = ref([]);
		const route = useRoute();
		const babbles = ref([]);

		onBeforeMount(async () => {
			const id = route.params.id ?? currentUser.value.id;

			let user = await getUser(id);
			user.data.avatar = `http://localhost:88/image/${user.data.avatar}`;
			user.data.background = `http://localhost:88/image/${user.data.background}`;
			profileUser.value = user.data;

			user.data.babbles.forEach(babble => {
				babble.user.avatar = `http://localhost:88/image/${babble.user.avatar}`;
				if (babble.rebabbleId !== null) {
					rebabbles.value.push(babble);
				} else {
					babbles.value.push(babble);
				}
			});

			profileUser.value.likeBabbles.forEach(likeBabble => {
				likeBabble.user.avatar = `http://localhost:88/image/${likeBabble.user.avatar}`;
			});

			if (profileUser.value.id === currentUser.value.id) {
				store.commit('SET_USER', user.data);
			}
		});

		const onFollow = () => {
			follow(profileUser.value.id);
			profileUser.value.followers.push(currentUser.value);

			sendFollowNotification(profileUser.value, currentUser.value);
		};

		const onUnFollow = () => {
			unfollow(profileUser.value.id);
			profileUser.value.followers = profileUser.value.followers.filter(
				f => f.id !== currentUser.value.id
			);
		};

		return {
			showProfileEditModal,
			currentUser,
			profileUser,
			currentTab,
			onUnFollow,
			rebabbles,
			onFollow,
			babbles,
			moment,
			router,
		};
	},
};
</script>

<style></style>
