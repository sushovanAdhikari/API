CREATE OR REPLACE PROCEDURE public.sp_update_status_removed_content(OUT error_message text)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    rec_id varchar;
   	log_info text;
   	log_record_id int;
begin
	
	for rec_id in (select ytube_playlist_id from playlist)
	loop 
		raise notice 'rec.id_for_type %',rec_id;
		if rec_id not in (select v.id_for_type from video_playlist_log v where v."type" = 'playlist') then
			update playlist set playlist_status = 0 where ytube_playlist_id = rec_id;
			
		 	select p.playlist_id into log_record_id from playlist p where p.ytube_playlist_id = rec_id;
			log_info := FORMAT('updated playlist:%s status to 0', rec_id::text);
			INSERT INTO public.trans_log_record
			(trans_table, trans_type, trans_info, trans_table_id)
			VALUES('playlist', 'update', log_info, log_record_id);

		end if;
	end loop;

	for rec_id in (select ytube_video_id from videos)
		loop 
			raise notice 'rec.id_for_type %',rec_id;
			if rec_id not in (select v.id_for_type from video_playlist_log v where v."type" = 'video') then
				update videos set video_status = 0 where ytube_video_id  = rec_id;
			end if;
		end loop;
	
	delete from video_playlist_log;
EXCEPTION
    WHEN others THEN
--       RAISE exception 'Error from blah blah: %', SQLERRM;
       error_message := sqlerrm;
END;
$procedure$
;
