import mongoose from 'mongoose';
import database from '../../../lib/database_ops/database';
import { UserProjects} from '../../../lib/database_ops/models';

await database.connect()
export const GET = async ({ url, request }: any) => {
	const req: string = request.headers.get('request');
	if(req === 'fetch_user_data') {
		let user_id = url.searchParams.get('_id')
		const data = await UserProjects.find({user: new mongoose.Types.ObjectId(user_id)}, {updatedAt:0}).sort({_id: -1}).limit(12)
		return new Response(JSON.stringify(data), { status: 200 });
	}
	if (req === 'fetch_users_data') {
		let skip = url.searchParams.get('skip') ?? 0;
		let limit = url.searchParams.get('limit') ?? 10;
		let total_count = url.searchParams.get('total_count') ?? false
		let total = 0;
		const data = await UserProjects.find({})
			.sort({_id:-1})
			.limit(limit)
			.skip(skip)
			.populate({ path: 'user', select: 'username avatar fullname' })
			.exec();
		if (total_count) total = await UserProjects.countDocuments({})
		return new Response(JSON.stringify({data, total}), { status: 200 });
	}
	return new Response('working....', { status: 200 });
};
