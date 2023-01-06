import { mvcInstance } from './index';

function insertBabble(babble) {
	return mvcInstance.post('babble', babble);
}

function deleteBabble(id) {
	return mvcInstance.delete(`/babble/${id}`);
}

function getBabble(id) {
	return mvcInstance.get(`/babble/${id}`);
}

function getBabbles() {
	return mvcInstance.get('babbles');
}

function getBabblesWithTag(tag) {
	return mvcInstance.get(`babbles/${tag}`);
}

function getBabblesWithId(id) {
	return mvcInstance.get(`user/${id}/babbles`);
}

function insertRebabble(babble) {
	return mvcInstance.post('rebabble', babble);
}

function getUser(id) {
	return mvcInstance.get(`user/${id}`);
}

function getMyInfo() {
	return mvcInstance.get('my');
}

function insertComment(babbleId, comment) {
	return mvcInstance.post(`babble/${babbleId}/comment`, comment);
}

function deleteComment(babbleId, commentId) {
	return mvcInstance.delete(`babble/${babbleId}/comment/${commentId}`);
}

function like(id) {
	return mvcInstance.post(`babble/${id}/like`);
}

function unlike(id) {
	return mvcInstance.delete(`babble/${id}/like`);
}

function follow(id) {
	return mvcInstance.post(`user/${id}/follow`);
}

function unfollow(id) {
	return mvcInstance.delete(`user/${id}/follow`);
}

export {
	insertBabble,
	deleteBabble,
	getBabble,
	getBabbles,
	getBabblesWithTag,
	insertRebabble,
	getUser,
	insertComment,
	like,
	unlike,
	deleteComment,
	follow,
	unfollow,
	getMyInfo,
	getBabblesWithId,
};
