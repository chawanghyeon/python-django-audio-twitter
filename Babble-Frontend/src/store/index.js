import createPersistedState from 'vuex-persistedstate';
import { createStore } from 'vuex';

const store = createStore({
	state() {
		return {
			user: null,
			tags: null,
			token: null,
			username: null,
			password: null,
			checkedAudio: null,
			isCommentModal: false,
		};
	},
	mutations: {
		SET_USER: (state, user) => {
			state.user = user;
		},
		CLEAR_DATA: state => {
			state.user = null;
			state.tags = null;
			state.token = null;
			state.username = null;
			state.password = null;
			state.checkedAudio = null;
			state.isCommentModal = false;
		},
		SET_TOKEN(state, token) {
			state.token = token;
		},
		SET_CHECKEDAUDIO(state, checkedAudio) {
			state.checkedAudio = checkedAudio;
		},
		SET_USERNAME(state, username) {
			state.username = username;
		},
		SET_PASSWORD(state, password) {
			state.password = password;
		},
		SET_TAGS(state, tags) {
			state.tags = tags;
		},
		SET_ISCOMMENTMODAL(state, isCommentModal) {
			state.isCommentModal = isCommentModal;
		},
	},
	plugins: [createPersistedState()],
});

export default store;
