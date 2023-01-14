<template>
	<!-- notification -->
	<div class="flex-1 border-r border-gray-100 flex flex-col overflow-y-auto">
		<!-- title -->
		<div class="p-3 font-bold text-lg border-b border-gray-100">알림</div>
		<!-- notifications -->
		<div
			class="flex flex-col hover:bg-gray-50 p-3 space-y-2 border-b border-gray-100 cursor-pointer"
			v-for="notification in notifications"
			:key="notification.sender_id"
		>
			<div class="flex justify-between">
				<router-link :to="`/profile/${notification._source.sender}`">
					<img
						:src="notification._source.sender_avatar"
						class="w-10 h-10 rounded-full hover:opacity-80"
					/>
				</router-link>
				<i
					class="fas fa-ellipsis-h text-gray-500 hover:bg-blue-50 hover:text-primary p-2 rounded-full w-10 h-10 flex items-center justify-center"
				></i>
			</div>
			<router-link
				v-if="notification._source.babble"
				:to="`/babble/${notification._source.babble}`"
				class="font-bold"
				>{{ notification._source.message }}</router-link
			>
			<router-link
				v-else
				:to="`/profile/${notification._source.sender}`"
				class="font-bold"
				>{{ notification._source.message }}</router-link
			>
		</div>
	</div>
</template>

<script>
import { getNotifications } from '../api/babbleElasticsearch.js';
import { computed, onBeforeMount, ref } from 'vue';
import store from '../store';

export default {
	setup() {
		const currentUser = computed(() => store.state.user);
		const notifications = ref([]);

		onBeforeMount(async () => {
			const result = await getNotifications(currentUser.value.id);
			notifications.value = result.data.hits.hits;
		});

		return {
			currentUser,
			notifications,
		};
	},
};
</script>

<style></style>
