import { fluxInstance } from './index';

const config = { headers: { 'Content-Type': 'multipart/form-data' } };

function getAudio() {
	return fluxInstance.get(`audio`);
}

function getImage() {
	return fluxInstance.get(`image`);
}

function saveImage(formData) {
	return fluxInstance.post('image', formData, config);
}

export { getAudio, getImage, saveImage };
