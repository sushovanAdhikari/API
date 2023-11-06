CREATE OR REPLACE PROCEDURE public.sp_insert_or_update_videolist(IN v_ytube_video_id text, IN v_video_title text, IN v_video_desc text, IN v_channel_name character varying, IN v_channel_id text, IN v_playlist_id integer, OUT error_message text)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    action text;
   	v_ytube_video_id text := v_ytube_video_id;
    v_video_title text := v_video_title;
    v_video_desc text := v_video_desc;
    v_channel_name varchar := v_channel_name;
    v_channel_id text := v_channel_id;
    v_playlist_id int := v_playlist_id;
    v_video_id int;
BEGIN
    -- Check if the record already exists based on a condition (e.g., playlist_id)
    if not EXISTS (SELECT 1 FROM videos WHERE ytube_video_id = v_ytube_video_id) THEN
        -- Set the action to "update" if the record exists
        action := 'insert';
    END IF;

    -- Perform the action based on the variable
	if action = 'insert' then
        INSERT INTO public.videos
		(ytube_video_id, video_title, video_description, channel_name, channel_id, video_status)
		VALUES(v_ytube_video_id, v_video_title, v_video_desc, v_channel_name, v_channel_id, 1);
		
		select video_id into v_video_id from public.videos where ytube_video_id = v_ytube_video_id;
		
		INSERT INTO public.playlistvideos
		(playlist_id, video_id, video_title, video_desc, channel_name, channel_id)
		VALUES(v_playlist_id, v_video_id, v_video_title, v_video_desc, v_channel_name, v_channel_id);
    END if;
    insert into video_playlist_log(type, id_for_type) values ('video', v_ytube_video_id);
EXCEPTION
    WHEN others THEN
        -- Handle errors related to the INSERT into public.playlistvideos
        -- You can log the error, raise a notice, or take other actions as needed
        error_message := SQLERRM;
        
        -- Rollback to a savepoint to isolate the error
--        ROLLBACK TO savepoint_name;
END;
$procedure$
;
