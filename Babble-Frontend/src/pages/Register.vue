<template>
	<div class="flex flex-col items-center space-y-4 mt-10">
		&nbsp;
		<br />
		<img
			src="../logo/6.jpg"
			width="300"
			height="300"
			class="text-4xl text-primary"
		/>
		<span class="text-2xl font-bold">회원가입</span>
		<input
			v-model="username"
			type="text"
			class="rounded w-96 px-4 py-3 border border-gray-300 focus:ring-2 focus:border-primary focus:outline-none"
			placeholder="이메일"
		/>
		<input
			v-model="nickname"
			type="text"
			class="rounded w-96 px-4 py-3 border border-gray-300 focus:ring-2 focus:border-primary focus:outline-none"
			placeholder="닉네임"
		/>
		<input
			v-model="firstName"
			type="text"
			class="rounded w-96 px-4 py-3 border border-gray-300 focus:ring-2 focus:border-primary focus:outline-none"
			placeholder="이름"
		/>
		<input
			v-model="lastName"
			type="text"
			class="rounded w-96 px-4 py-3 border border-gray-300 focus:ring-2 focus:border-primary focus:outline-none"
			placeholder="성"
		/>
		<input
			@keyup.enter="onRegister"
			v-model="password"
			type="password"
			class="rounded w-96 px-4 py-3 border border-gray-300 focus:ring-2 focus:border-primary focus:outline-none"
			placeholder="비밀번호"
		/>
		<button v-if="loading" class="w-96 rounded bg-light text-white py-3">
			회원가입 중입니다.
		</button>
		<button
			v-else
			class="w-96 rounded bg-primary text-white py-3 hover:bg-dark"
			@click="onRegister"
		>
			회원가입
		</button>
		<router-link to="/login">
			<button class="text-primary">계정이 이미 있으신가요? 로그인 하기</button>
		</router-link>
	</div>
</template>

<script>
import { validateEmail } from '../utils/validation.js';
import { useRouter } from 'vue-router';
import { signUp } from '../api/auth.js';
import { ref } from 'vue';

export default {
	setup() {
		const username = ref('');
		const nickname = ref('');
		const firstName = ref('');
		const lastName = ref('');
		const password = ref('');
		const loading = ref(false);
		const router = useRouter();

		const onRegister = async () => {
			if (
				!username.value ||
				!nickname.value ||
				!firstName.value ||
				!lastName.value ||
				!password.value
			) {
				alert('빈칸을 모두 입력해주세요.');
				return;
			}

			let isValidate = validateEmail(username.value);

			if (!isValidate) {
				alert('이메일 형식이 맞지 않습니다.');
				return;
			}

			loading.value = true;

			const data = {
				username: username.value,
				nickname: nickname.value,
				firstName: firstName.value,
				lastName: lastName.value,
				password: password.value,
			};

			signUp(data);
			loading.value = false;

			router.push('/login');
		};

		return {
			onRegister,
			firstName,
			username,
			nickname,
			lastName,
			password,
			loading,
		};
	},
};
</script>

<style></style>
