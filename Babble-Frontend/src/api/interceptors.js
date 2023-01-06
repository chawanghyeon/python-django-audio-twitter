import { signIn } from './auth.js';
import store from '../store/index';

export function setInterceptors(instance) {
	// Add a request interceptor
	instance.interceptors.request.use(
		function (config) {
			// Do something before request is sent
			// console.log(config);
			config.headers.Authorization = store.state.token;
			return config;
		},
		function (error) {
			// Do something with request error
			return Promise.reject(error);
		}
	);

	// Add a response interceptor
	instance.interceptors.response.use(
		function (response) {
			// Any status code that lie within the range of 2xx cause this function to trigger
			// Do something with response data
			return response;
		},
		async function (error) {
			const originalRequest = error.config;
			if (error.response.status === 403 && !originalRequest._retry) {
				console.log('토큰 만료');
				originalRequest._retry = true;
				if (store.state.username && store.state.password) {
					const userInfo = {
						username: store.state.username,
						password: store.state.password,
					};
					const response = await signIn(userInfo);
					if (response) {
						await store.commit('SET_TOKEN', response.headers['authorization']);
						originalRequest.headers['Authorization'] = store.state.token;
					}
					return instance(originalRequest);
				} else {
				}
			}
			if (error.response.status === 500) {
				window.location.href = '/login';
			}
			return Promise.reject(error);
		}
	);
	return instance;
}
