import { setInterceptors } from './interceptors';
import axios from 'axios';

function createInstance(url) {
	return axios.create({
		baseURL: url,
	});
}

// 엑시오스 초기화 함수
function createInstanceWithAuth(url) {
	const instance = axios.create({
		baseURL: url,
	});
	return setInterceptors(instance);
}

export const instance = createInstance('http://localhost:80');
export const flaskInstance = createInstance('http://localhost:5000');
export const mvcInstance = createInstanceWithAuth('http://localhost:80');
export const fluxInstance = createInstanceWithAuth('http://localhost:88');
export const elInstance = createInstance('http://localhost:9200');
