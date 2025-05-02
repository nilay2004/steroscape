import mongoose, { model } from 'mongoose';
// mongoose.set('strictQuery', true);
const UsersSchema = new mongoose.Schema(
	{
		fullname: { type: String, required: true },
		username: { type: String, required: true },
		email: { type: String, required: true },
		passion: { type: String, required: false },
		avatar: { type: String, required: false },
		password: { type: String, required: true }
	},
	{ timestamps: true }
);
const visitorsSchema = new mongoose.Schema(
	{
		ip: { type: String, required: true },
		visits: { type: Number, required: true }
	},
	{
		timestamps: true,
		strict: false
	}
);
const UsersDataSchema = new mongoose.Schema(
	{
		user: { type: mongoose.Types.ObjectId, required: true, ref: 'users' },
		images: { type: Array, default: [], required: false },
		dataset: { type: String, required: false, defualt: '' },
		model: { type: String, required: false, default: '' },
		video: {type: String, required:false},
		psnrs: {type: Array, required:false},
		size: {type: Object, required: false, default: {images: 0, dataset: 0, models: 0}}
	},
	{ timestamps: true }
);
export const Users: any = mongoose.models.users || mongoose.model('users', UsersSchema);
export const UserProjects:any = mongoose.models.user_project || mongoose.model('user_project', UsersDataSchema)
export const Visitors:any = mongoose.models.visitors || mongoose.model('visitors', visitorsSchema)
