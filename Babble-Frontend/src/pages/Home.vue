<template>
	<!-- main part -->
	<div class="flex-1 border-r border-gray-100 overflow-y-auto">
		<div class="flex flex-col">
			<!-- page title -->
			<div class="border-b border-gray-100 px-3 py-2 font-bold text-lg">홈</div>
			<!-- babbleing section -->
			<div class="flex px-3 py-3 border-b-8 border-gray-100">
				<img
					v-if="$store.state.user.avatar.slice(-4) !== 'null'"
					:src="$store.state.user.avatar"
					class="w-10 h-10 rounded-full hover:opacity-80 cursor-pointer"
				/>
				<img
					v-else
					src="../image/defaultProfile.png"
					class="w-10 h-10 rounded-full hover:opacity-80 cursor-pointer"
				/>
				<div class="ml-2 flex-1 flex flex-col">
					<audio-recorder @insert-babble="insertNewBabble" />
				</div>
			</div>
			<!-- babbles -->
			<Babble
				:currentUser="currentUser"
				:babble="babble"
				v-for="babble in babbles"
				:key="babble.id"
				@delete="onDeleteBabble"
				@unrebabble="onDeleteRebabble"
				@rebabble="oninsertRebabble"
			/>
		</div>
	</div>
</template>

<script>
import AudioRecorder from '../components/audioRecorder/recorder.vue';
import Babble from '../components/Babble.vue';
import store from '../store';
import { getBabbles, getBabblesWithTag } from '../api/babble';
import { ref, computed, onBeforeMount } from 'vue';

export default {
	components: { Babble, AudioRecorder },
	watch: {
		async '$route.params.tag'(val) {
			let data = await getBabblesWithTag(val);
			this.babbles = data.data;
			this.babbles.forEach(babble => {
				babble.user.avatar = `http://localhost:88/image/${babble.user.avatar}`;
			});
		},
	},
	methods: {
		onDeleteBabble(babble) {
			this.babbles = this.babbles.filter(t => t !== babble);
		},
		onDeleteRebabble(babbleId) {
			this.babbles = this.babbles.filter(t => t.id !== babbleId);
		},
		oninsertRebabble(babble) {
			this.babbles.push(babble);
		},
		insertNewBabble: function (babble) {
			this.babbles.push(babble);
		},
	},
	setup() {
		const currentUser = computed(() => store.state.user);
		const babbles = ref([]);

		onBeforeMount(async () => {
			const response = await getBabbles();
			babbles.value = response.data;
			babbles.value.forEach(babble => {
				babble.user.avatar = `http://localhost:88/image/${babble.user.avatar}`;
			});
		});

		return { currentUser, babbles };
	},
};
</script>

<style></style>
