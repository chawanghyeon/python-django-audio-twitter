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
		<input
			v-model="email"
			type="text"
			class="rounded w-96 px-4 py-3 border border-gray-300 focus:ring-2 focus:border-primary focus:outline-none"
			placeholder="이메일"
		/>
		<input
			@keyup.enter="onLogin"
			v-model="password"
			type="password"
			class="rounded w-96 px-4 py-3 border border-gray-300 focus:ring-2 focus:border-primary focus:outline-none"
			placeholder="비밀번호"
		/>
		<button v-if="loading" class="w-96 rounded bg-light text-white py-3">
			로그인 중입니다.
		</button>
		<button
			v-else
			class="w-96 rounded bg-primary text-white py-3 hover:bg-dark"
			@click="onLogin"
		>
			로그인
		</button>
		<router-link to="/register">
			<button class="text-primary">계정이 없으신가요? 회원가입 하기</button>
		</router-link>
	</div>
</template>

<script>
import AudioRecorder from '../components/audioRecorder/recorder.vue';
import store from '../store/index';
import { useRouter } from 'vue-router';
import { getMyInfo } from '../api/babble';
import { signIn } from '../api/auth';
import { ref } from 'vue';

export default {
	components: { AudioRecorder },
	setup() {
		const email = ref('');
		const password = ref('');
		const loading = ref(false);
		const router = useRouter();

		const onLogin = async () => {
			if (!email.value || !password.value) {
				alert('이메일, 비밀번호를 모두 입력해주세요.');
				return;
			}

			loading.value = true;

			const userData = {
				username: email.value,
				password: password.value,
			};

			store.commit('SET_USERNAME', email.value);
			store.commit('SET_PASSWORD', password.value);

			const data = await signIn(userData);

			await store.commit('SET_TOKEN', data.headers['authorization']);
			const doc = await getMyInfo();

			doc.data.avatar = `http://localhost:88/image/${doc.data.avatar}`;
			doc.data.background = `http://localhost:88/image/${doc.data.background}`;

			store.commit('SET_USER', doc.data);
			loading.value = false;
			router.replace('/');
		};

		return {
			email,
			password,
			loading,
			onLogin,
		};
	},
};
</script>

<style></style>
