import { createRouter, createWebHistory } from 'vue-router';
import Notifications from '../pages/Notifications.vue';
import Register from '../pages/Register.vue';
import Profile from '../pages/Profile.vue';
import Babble from '../pages/Babble.vue';
import Login from '../pages/Login.vue';
import Home from '../pages/Home.vue';
import store from '../store';

const routes = [
	{
		path: '/',
		name: 'home',
		component: Home,
		title: '홈',
		icon: 'fas fa-home fa-fw text-2xl',
		meta: { isMenu: true, layout: 'DefaultLayout', requireAuth: true },
	},
	{
		path: '/notifications',
		name: 'notifications',
		component: Notifications,
		title: '알림',
		icon: 'far fa-bell fa-fw text-2xl',
		meta: { isMenu: true, layout: 'DefaultLayout', requireAuth: true },
	},
	{
		path: '/profile',
		name: 'profile',
		component: Profile,
		title: '프로필',
		icon: 'far fa-user fa-fw text-2xl',
		meta: { isMenu: true, layout: 'DefaultLayout', requireAuth: true },
	},
	{
		path: '/profile/:id',
		component: Profile,
		meta: { isMenu: false, layout: 'DefaultLayout', requireAuth: true },
	},
	{
		path: '/babble/:id',
		name: 'babble',
		component: Babble,
		meta: { isMenu: false, layout: 'DefaultLayout', requireAuth: true },
	},
	{
		path: '/:tag',
		component: Home,
		meta: { isMenu: false, layout: 'DefaultLayout', requireAuth: true },
	},
	{
		path: '/register',
		name: 'register',
		component: Register,
		meta: { isMenu: false, layout: 'EmptyLayout' },
	},
	{
		path: '/login',
		name: 'login',
		component: Login,
		meta: { isMenu: false, layout: 'EmptyLayout' },
	},
];

const router = createRouter({
	mode: 'history',
	history: createWebHistory(),
	routes,
});

// navigation guard
router.beforeEach((to, from, next) => {
	const requireAuth = to.matched.some(record => record.meta.requireAuth);
	// not authenticated
	if (requireAuth && !store.state.user) next('/login');
	// authenticated
	else next();
});

export default router;
