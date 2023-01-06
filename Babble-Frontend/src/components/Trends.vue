<template>
	<div class="hidden lg:block lg:w-2/5 px-4 py-2">
		<!--babble search  input -->
		<div class="relative mb-5">
			<input
				v-model="hashTag"
				@keyup.enter="search"
				placeholder="Hash Tag"
				type="text"
				class="pl-10 rounded-full w-full p-2 bg-gray-100 text-sm focus:ring-1 focus:ring-primary focus:bg-white focus:outline-none"
			/>
			<i class="fas fa-search absolute left-0 mt-2 ml-3 text-sm text-light"></i>
		</div>
		<!-- trend for me -->
		<div class="w-full rounded-xl bg-gray-50 flex flex-col">
			<div
				class="flex items-center justify-between px-3 py-1 border-b border-gray-100"
			>
				<span class="text-lg font-bold">최근 내가 많이 사용한 단어들</span>
			</div>
			<iframe src="http://localhost:5601/app/dashboards#/view/1a09ac70-a343-11eb-b490-43c22c963dbd?embed=true&_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!f%2Cvalue%3A10000)%2Ctime%3A(from%3Anow-1h%2Cto%3Anow))&hide-filter-bar=true" height="380"></iframe>
		</div>
		<!-- follow recommends -->
		<div class="mt-5 w-full rounded-xl bg-gray-50 flex flex-col">
			<div class="px-3 py-3 border-b border-gray-100">
				<span class="text-lg font-bold">최근 나의 상태</span>
			</div>
			<iframe src="http://localhost:5601/app/dashboards#/view/c31e20c0-a343-11eb-b490-43c22c963dbd?embed=true&_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!f%2Cvalue%3A10000)%2Ctime%3A(from%3Anow-1h%2Cto%3Anow))&hide-filter-bar=true" height="490"></iframe>
		</div>
	</div>
</template>

<script>
import { useRouter } from 'vue-router';

export default {
	data: function () {
		return {
			hashTag: '',
			router: useRouter(),
		};
	},
	methods: {
		search: function () {
			this.$data.router.replace(`/${this.$data.hashTag}`);
		},
	},
};
</script>

<style></style>
