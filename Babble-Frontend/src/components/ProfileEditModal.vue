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
					<div class="flex items-center">
						<button
							@click="$emit('close-modal')"
							class="flex items-center justify-center fas fa-times text-primary text-lg p-2 h-10 w-10 hover:bg-blue-50 rounded-full"
						></button>
						<span class="font-bold text-lg">프로필 수정</span>
					</div>
					<div class="text-right mr-2">
						<button
							@click="onSaveProfile"
							class="hover:bg-dark bg-primary text-white font-bold px-3 py-1 rounded-full"
						>
							저장
						</button>
					</div>
				</div>
				<!-- image section -->
				<div class="h-60">
					<!-- background image -->
					<div
						class="bg-gray-300 h-40 relative flex-none flex items-center justify-center"
					>
						<img
							ref="backgroundImage"
							:src="$store.state.user.background"
							class="object-cover absolute h-full w-full"
						/>
						<button
							@click="onChangeBackgroundImage"
							class="absolute h-10 w-10 hover:text-gray-200 rounded-full fas fa-camera text-white text-lg"
						></button>
						<input
							@change="previewBackgroundImage"
							type="file"
							accept="image/*"
							id="backgroundImageInput"
							class="hidden"
						/>
						<!-- profile image -->
						<img
							ref="profileImage"
							:src="$store.state.user.avatar"
							class="border-4 border-white w-28 h-28 absolute -bottom-14 left-2 rounded-full"
						/>
						<button
							@click="onChangeProfileImage"
							class="absolute -bottom-5 left-11 h-10 w-10 hover:text-gray-200 rounded-full fas fa-camera text-white text-lg"
						></button>
						<input
							@change="previewProfileImage"
							type="file"
							accept="image/*"
							id="profileImageInput"
							class="hidden"
						/>
					</div>
				</div>

				<div class="flex flex-col p-2">
					<div
						class="mx-2 my-1 px-2 py-1 border text-gray border-gray-200 rounded hover:border-primary hover:text-primary"
					>
						<input
							type="text"
							v-model="$store.state.user.nickname"
							placeholder="닉네임"
							class="text-black focus:outline-none"
						/>
					</div>
					<div
						class="mx-2 my-1 px-2 py-1 border text-gray border-gray-200 rounded hover:border-primary hover:text-primary"
					>
						<input
							type="text"
							v-model="$store.state.user.bio"
							placeholder="한줄소개"
							class="text-black focus:outline-none"
						/>
					</div>
					<div
						class="mx-2 my-1 px-2 py-1 border text-gray border-gray-200 rounded hover:border-primary hover:text-primary"
					>
						<input
							type="text"
							v-model="$store.state.user.firstName"
							placeholder="이름"
							class="text-black focus:outline-none"
						/>
					</div>
					<div
						class="mx-2 my-1 px-2 py-1 border text-gray border-gray-200 rounded hover:border-primary hover:text-primary"
					>
						<input
							type="text"
							v-model="$store.state.user.lastName"
							placeholder="성"
							class="text-black focus:outline-none"
						/>
					</div>
					<div
						class="mx-2 my-1 px-2 py-5 border text-gray border-gray-200 rounded hover:border-primary hover:text-primary"
					>
						<input
							type="text"
							v-model="$store.state.user.phoneNumber"
							placeholder="핸드폰 번호"
							class="text-black focus:outline-none"
						/>
					</div>
					<div
						class="mx-2 my-1 px-2 py-3 border text-gray border-gray-200 rounded hover:border-primary hover:text-primary"
					>
						<select v-model="$store.state.user.gender">
							<option value="male">Male</option>
							<option value="female">Female</option>
							<option value="whatever">Whatever</option>
						</select>
					</div>
					<div
						class="mx-2 my-1 px-2 py-3 border text-gray border-gray-200 rounded hover:border-primary hover:text-primary"
					>
						<input
							type="date"
							placeholder="생년월일"
							v-model="$store.state.user.birth"
							class="text-black focus:outline-none"
						/>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { updateUserInfo } from '../api/auth.js';
import { saveImage } from '../api/babbleSteam.js';
import { ref } from 'vue';
import store from '../store';

export default {
	setup(props, { emit }) {
		const profileImage = ref(null);
		const profileImageData = ref(null);
		const backgroundImage = ref(null);
		const backgroundImageData = ref(null);

		const onChangeBackgroundImage = () => {
			document.getElementById('backgroundImageInput').click();
		};

		const onChangeProfileImage = () => {
			document.getElementById('profileImageInput').click();
		};

		const getImageName = () => {
			const date = new Date();
			if (date.getMonth() + 1 < 10) {
				let name = `${store.state.user.username}.${date.getFullYear()}-0${
					date.getMonth() + 1
				}-${date.getDate()}-${date.getHours()}-${date.getMinutes()}-${date.getSeconds()}-${date.getMilliseconds()}.jpeg`;
				return name;
			} else {
				let name = `${store.state.user.username}.${date.getFullYear()}-${
					date.getMonth() + 1
				}-${date.getDate()}-${date.getHours()}-${date.getMinutes()}-${date.getSeconds()}-${date.getMilliseconds()}.jpeg`;
				return name;
			}
		};

		const previewBackgroundImage = event => {
			const file = event.target.files[0];

			backgroundImageData.value = new File([file], getImageName(), {
				type: file.type,
				lastModified: file.lastModified,
			});

			const reader = new FileReader();
			reader.onload = function (event) {
				backgroundImage.value.src = event.target.result;
			};
			reader.readAsDataURL(file);
		};

		const previewProfileImage = async event => {
			const file = event.target.files[0];

			profileImageData.value = new File([file], getImageName(), {
				type: file.type,
				lastModified: file.lastModified,
			});

			const reader = new FileReader();
			reader.onload = function (event) {
				profileImage.value.src = event.target.result;
			};
			reader.readAsDataURL(file);
		};

		const onSaveProfile = () => {
			const tempUser = store.state.user;

			if (profileImageData.value) {
				tempUser.avatar = profileImageData.value.name;
				const formData = new FormData();
				formData.append('image', profileImageData.value);

				saveImage(formData);
			} else {
				tempUser.avatar = tempUser.avatar.slice(26);
			}

			if (backgroundImageData.value) {
				tempUser.background = backgroundImageData.value.name;
				const formData = new FormData();
				formData.append('image', backgroundImageData.value);

				saveImage(formData);
			} else {
				tempUser.background = tempUser.background.slice(26);
			}

			updateUserInfo(tempUser);
			emit('close-modal');
		};

		return {
			onChangeBackgroundImage,
			previewBackgroundImage,
			onChangeProfileImage,
			previewProfileImage,
			backgroundImageData,
			profileImageData,
			backgroundImage,
			onSaveProfile,
			profileImage,
		};
	},
};
</script>

<style></style>
